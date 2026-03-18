import queue
import weakref
import re
import socket

from nicegui import ui, run
import llm_server as llms
import llm

from llm_server.helper.helper import Endpoint
from llm_server.helper.gui_helper import LocalFilePicker


class LlmServerWidget:

    def __init__(self) -> None:

        self.server: llms.Server = None
        self.network: Network = None
        self.model_table: ModelTable = None

        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self.log_area: ui.textarea = None
        self.log_timer: ui.timer = None
        self.log_button: ui.button = None

        with ui.card().classes('w-[40rem]'):
            ui.label(text='LLM Server').classes('text-lg font-medium w-full text-center')

            ui.separator()

            self.network = Network(parent=self)
            self.server = llms.Server()
            self.server.set_host(ip_address=self.network.ip_address.value, port=int(self.network.port.value))

            ui.separator()

            with ui.tabs().classes('w-full') as self.tabs:
                tab_selection = ui.tab('Selection')
                tab_loading = ui.tab('Loading')

            with ui.tab_panels(self.tabs, value=tab_selection).classes('w-full'):
                with ui.tab_panel(tab_selection):
                    self.model_table = ModelTable(parent=self)
                with ui.tab_panel(tab_loading):
                    self.model_loading = ModelLoading(parent=self)

            self.log_area = ui.textarea(
                label='Log',
                placeholder='Logs will appear here...',
                value=''
                ).props('readonly').classes('w-full').style('height: 220px; overflow:auto;')

            self.log_button = ui.button(
                text='Clear Log',
                on_click=self.clear_log,
            ).props('push color=primary')

        self.log_timer = ui.timer(
            interval=0.2,
            callback=self.flush_logs,
            active=True)


    def flush_logs(self) -> None:
        while True:
            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self.log_area.value = (self.log_area.value + line + '\n').lstrip()

        return


    def clear_log(self) -> None:
        self.log_area.value = ''
        return


class Network:

    def __init__(self, parent: LlmServerWidget) -> None:

        self.parent = weakref.proxy(parent)

        self.endpoint: Endpoint = None

        self.by_id: dict = {}

        self.on_off: ui.button = None
        self.ip_address: ui.input = None
        self.port: ui.input = None

        ui.label(text='Endpoint').classes('text-md font-meeium')
        with ui.row().classes('items-center gap-4'):
            self.on_off = ui.button(
                text='OFF',
                on_click=self.on_toggle
                ).props('push color=grey outline')

            with ui.column().classes('gap-1'):
                self.ip_address = ui.input(
                    label='IP Address',
                    value='127.0.0.1',
                    placeholder='127.0.0.1',  # NOTE: Value supercededs placeholder.
                    ).props('dense outlined clearable').classes('w-[10rem]')
                self.ip_address.on('change', lambda e: self.on_ip_change(e))
                self.ip_address.on('clear', lambda e: self.on_off.disable())
                self.by_id[self.ip_address.id] = self.ip_address

            ui.label(':').classes('pt-2 text-lg')

            with ui.column().classes('gap-1'):
                self.port = ui.input(
                    label='Port',
                    value='8000',
                    placeholder='8000',
                    ).props('dense outlined clearable type=number').classes('w-[8rem]')
                self.port.on('change', lambda e: self.on_port_change(e))
                self.port.on('clear', lambda e: self.on_off.disable())
                self.by_id[self.port.id] = self.port

            if not self.is_endpoint_free(ip_address=self.ip_address.value, port=int(self.port.value)):
                self.on_off.disable()


    def on_toggle(self) -> None:

        if self.parent.server.is_online:
            self.parent.server.stop()
            self.on_off.text = 'OFF'
            self.on_off.props('push color=red outline')
        else:
            self.parent.server.set_host(ip_address=self.ip_address.value, port=int(self.port.value))
            self.parent.server.start()

            if self.parent.server.is_online:
                self.on_off.text = 'ON'
                self.on_off.props('push color=green')
            else:
                self.parent.log_queue.put('Server failed to start.')

        return


    def on_port_change(self, e) -> None:
        MAX_PORT = 65535

        is_valid_port = lambda port: (0 <= port <= MAX_PORT)

        port = int(self.port.value)

        if not is_valid_port(port):
            self.port.value = 8000  # Reset to valid option.
            self.parent.log_queue.put(f'Invalid port. Must be integer 1-{MAX_PORT}.')
            self.on_off.disable()
            return

        if self.is_endpoint_free(ip_address=self.ip_address.value, port=port):
            self.on_off.enable()
        else:
            self.on_off.disable()

        return


    def on_ip_change(self, e) -> None:

        is_valid_ip_address = lambda ip_address: bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_address))

        ip_address = str(self.ip_address.value).strip()

        if not is_valid_ip_address(ip_address):
            self.parent.log_queue.put(f'Invalid IP address. Must be format "X.X.X.X".')
            self.ip_address.value = '127.0.0.1'  # Reset to something normal.
            self.on_off.disable()
            return

        if self.is_endpoint_free(ip_address=ip_address, port=int(self.port.value)):
            self.on_off.enable()
        else:
            self.on_off.disable()

        return


    @staticmethod
    def is_endpoint_free(ip_address: str, port: int) -> bool:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((ip_address, port))
                return True
            except OSError:
                return False
        return



class ModelTable:

    def __init__(self, parent: LlmServerWidget) -> None:

        self.parent = weakref.proxy(parent)
        
        self.table: ui.table = None

        self.new_tag_input: str = None
        self.new_name_input: ui.select = None

        self.by_id: dict = {}

        self._selected_models: list = []

        ui.label(text='Models').classes('text-md font-medium')
        with ui.row().classes('items-center gap-4 w-full'):
            self.table = ui.table(
                columns=[
                    {'name': 'tag', 'label': 'Tag', 'field': 'tag', 'align': 'left'},
                    {'name': 'model', 'label': 'Model', 'field': 'model', 'align': 'left'}],
                rows=[],
                row_key='key',
                ).props('selection="multiple"').classes('w-full').style('max-height: 220px; overflow:auto;')
            self.table.on('selection', self.on_table_selection)

        with ui.row().classes('items-center gap-3 mt-2'):
            with ui.column().classes('gap-1'):
                self.new_tag_input = ui.input(
                    label='Tag',
                    placeholder='Phi-4',
                    value=''
                    ).props('dense outlined clearable').classes('w-[8rem]')
                self.new_tag_input.on('change', lambda e: self.on_tag_change(e))
                self.by_id[self.new_tag_input.id] = self.new_tag_input

            ui.label(':').classes('pt-2 text-lg')

            with ui.column().classes('gap-1'):
                self.new_name_input = ui.select(
                    options=llm.list_models(kind='llm'),
                    label='Model',
                    ).props('outlined dense').classes('w-[18rem]')
                self.new_name_input.on('change', lambda e: self.on_name_change(e))
                self.by_id[self.new_name_input.id] = self.new_name_input

            ui.button(text='+ Add', on_click=self.on_add_model).props('push color=secondary')
            ui.button(text='Remove Selected', on_click=self.on_remove_selected).props('push color=negative outline')


    def _rows_from_table(self) -> list[dict]:
        model_list = self.parent.server.backend.models
        current_models = [{'key': i, 'tag': k, 'model': model_list[k].name} for i, k in enumerate(model_list)]

        return current_models


    def _refresh_table(self) -> None:
        self.table.rows = self._rows_from_table()
        self.table.update()
        return


    def on_tag_change(self, e) -> None:
        if not isinstance(self.new_tag_input.value, str):
            self.parent.log_queue.put(f'Invalid model tag. Must be string.')
            self.new_tag_input = ''

        return


    def on_add_model(self) -> None:
        tag = str(self.new_tag_input.value).strip()
        name = str(self.new_name_input.value).strip()
        if not tag or not name:
            self.parent.log_queue.put('Both "Tag" and "Name" fields are required to add a model.')
            return

        if tag in self.parent.server.backend.models:
            self.parent.log_queue.put(f'A model by tag "{tag}" already exists.')
            return

        self.parent.server.add_model(tag=tag, name=name)

        self._refresh_table()

        self.new_tag_input.value = ''
        self.new_name_input.value = ''

        self.parent.model_loading.model_select.options = list(self.parent.server.backend.models.keys())
        self.parent.model_loading.model_select.update()

        self.parent.log_queue.put(f'Added model, {tag}: {name}')

        return


    def on_table_selection(self, e) -> None:
        currently_selected = self._selected_models

        selected = getattr(e, 'args', [])
        changed_items = [item['tag'] for item in selected['rows']]

        if selected['added']:
            self._selected_models.extend([tag for tag in changed_items if tag not in currently_selected])
        else:
            self._selected_models = [i for i in currently_selected if i not in changed_items]

        return


    def on_remove_selected(self) -> None:

        if not self._selected_models:
            self.parent.log_queue.put('No connections selected to remove.')
            return

        for tag in self._selected_models:
            self.parent.server.del_model(tag=tag)

        self._refresh_table()
        self._selected_models.clear()

        self.parent.model_loading.model_select.options = list(self.parent.server.backend.models.keys())
        self.parent.model_loading.model_select.update()

        self.parent.loq_queue.put(f'Removed model: {tag}')

        return


class ModelLoading:

    def __init__(self, parent: LlmServerWidget) -> None:

        self.parent = weakref.proxy(parent)

        self.by_id: dict = {}

        self.model_select: ui.select = None
        self.location: ui.input = None
        self.button_browse: ui.button = None
        self.button_load: ui.button = None

        with ui.row().classes('items-start gap-3'):
            ui.label('Select:').classes('pt-2 font-medium')

            self.model_select = ui.select(
                options=list(self.parent.server.backend.models.keys()),
                label='Model',
                on_change=self.on_model_select
                ).props('outlined dense').classes('w-[8rem]')

        with ui.row().classes('items-start gap-3'):

            ui.label('Location:').classes('pt-2 font-medium')

            self.location = ui.input(
                label='Model cache',
                placeholder='.../model cache',
                value='',
                ).props('dense outlined clearable').classes('w-[20rem]')
            self.location.on('change', lambda e: self.on_location_change(e))
            self.location.disable()

            self.button_browse = ui.button(
                text='Browse',
                on_click=self.on_browse).props('unelevated')
            self.button_browse.disable()

        with ui.row().classes('w-full gap-1 justify-center'):
            self.button_load = ui.button(
                text='Load',
                color='gold',
                on_click=self.on_load).props('unelevated')
            self.button_load.disable()


    def on_model_select(self, e):
        self.selected_model = e.value
        
        self.location.enable()
        self.button_browse.enable()
        self.button_load.enable()
        return


    def on_location_change(self, e):
        self.location.value = e.value
        return


    async def on_load(self, e):
        self.button_load.disable()
        self.parent.log_queue.put(f'Loading model "{self.selected_model}"...')
        await run.io_bound(self.parent.server.load_model, tag=self.selected_model, location=self.location.value)
        self.parent.log_queue.put(f'Model "{self.selected_model}" loaded.')

        self.location.enable()
        self.button_browse.enable()
        self.button_load.enable()

        return


    async def on_browse(self) -> None:
        import os
        start_dir = os.path.expanduser('~')
        file_path = await LocalFilePicker(start_dir, multiple=False)

        if not file_path:
            return

        self.location.value = file_path[0]
        self.location.update()

        return


def run_gui(ip_address: str='127.0.0.1', port: int=8000) -> None:

    def root():
        with ui.row().classes('w-full justify-center p-6'):
            LlmServerWidget()

    ui.run(title='LLM Server', host=ip_address, port=port, root=root)

    return