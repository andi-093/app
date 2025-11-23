import flet as ft
import json
import os
from datetime import datetime
import base64

# Clase Empresa (mejorada)
class Empresa:
    def __init__(self, nombre, servicio, telefono, direccion, detalles, foto=None, id=None):
        self.id = id if id else datetime.now().strftime("%Y%m%d%H%M%S")
        self.nombre = nombre
        self.servicio = servicio
        self.telefono = telefono
        self.direccion = direccion
        self.detalles = detalles
        self.foto = foto
        self.fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "servicio": self.servicio,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "detalles": self.detalles,
            "foto": self.foto,
            "fecha_registro": self.fecha_registro
        }
    
    @staticmethod
    def from_dict(data):
        empresa = Empresa(
            data["nombre"],
            data["servicio"],
            data["telefono"],
            data["direccion"],
            data["detalles"],
            data.get("foto"),
            data.get("id")
        )
        empresa.fecha_registro = data.get("fecha_registro", "")
        return empresa

# Sistema de almacenamiento
class AlmacenamientoEmpresas:
    ARCHIVO = "empresas_data.json"
    
    @staticmethod
    def guardar(inventario):
        try:
            data = [empresa.to_dict() for empresa in inventario]
            with open(AlmacenamientoEmpresas.ARCHIVO, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False
    
    @staticmethod
    def cargar():
        try:
            if os.path.exists(AlmacenamientoEmpresas.ARCHIVO):
                with open(AlmacenamientoEmpresas.ARCHIVO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [Empresa.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error al cargar: {e}")
        return []
    
    @staticmethod
    def exportar_txt(inventario):
        try:
            filename = f"empresas_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("LISTADO DE EMPRESAS REGISTRADAS\n")
                f.write("=" * 50 + "\n\n")
                
                for i, empresa in enumerate(inventario, start=1):
                    f.write(f"EMPRESA #{i}\n")
                    f.write(f"ID: {empresa.id}\n")
                    f.write(f"Nombre: {empresa.nombre}\n")
                    f.write(f"Servicio: {empresa.servicio}\n")
                    f.write(f"Teléfono: {empresa.telefono}\n")
                    f.write(f"Dirección: {empresa.direccion}\n")
                    f.write(f"Detalles: {empresa.detalles}\n")
                    f.write(f"Fecha de registro: {empresa.fecha_registro}\n")
                    f.write("-" * 50 + "\n\n")
                
                f.write(f"\nTotal de empresas: {len(inventario)}\n")
                f.write(f"Exportado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return filename
        except Exception as e:
            print(f"Error al exportar: {e}")
            return None

def main(page: ft.Page):
    page.title = "Registro de Empresas Pro"
    page.scroll = "adaptive"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Cargar empresas guardadas
    inventario = AlmacenamientoEmpresas.cargar()
    
    # Variable para almacenar la empresa en edición
    empresa_editando = [None]
    
    # Variable para almacenar la foto seleccionada
    foto_seleccionada = [None]
    
    # Campos de entrada
    nombre_field = ft.TextField(label="Nombre de la empresa", width=300)
    servicio_field = ft.TextField(label="Servicio que ofrece", width=300)
    telefono_field = ft.TextField(label="Teléfono", width=300, keyboard_type=ft.KeyboardType.PHONE)
    direccion_field = ft.TextField(label="Dirección", width=300)
    detalles_field = ft.TextField(
        label="Detalles del servicio",
        width=300,
        multiline=True,
        min_lines=3,
        max_lines=5
    )
    
    # Campo de búsqueda
    busqueda_field = ft.TextField(
        label="Buscar empresa...",
        width=300,
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: buscar_empresas(e.control.value)
    )
    
    # Contenedores
    lista_empresas = ft.Column(scroll="auto", spacing=10)
    mensaje = ft.Text("", size=14)
    imagen_preview = ft.Image(width=150, height=150, fit=ft.ImageFit.CONTAIN, visible=False)
    
    def limpiar_campos():
        nombre_field.value = ""
        servicio_field.value = ""
        telefono_field.value = ""
        direccion_field.value = ""
        detalles_field.value = ""
        foto_seleccionada[0] = None
        imagen_preview.visible = False
        empresa_editando[0] = None
        page.update()
    
    def seleccionar_foto(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            try:
                with open(file.path, "rb") as f:
                    foto_bytes = f.read()
                    foto_base64 = base64.b64encode(foto_bytes).decode()
                    foto_seleccionada[0] = foto_base64
                    imagen_preview.src_base64 = foto_base64
                    imagen_preview.visible = True
                    mensaje.value = "✅ Foto seleccionada"
                    mensaje.color = "green"
                    page.update()
            except Exception as ex:
                mensaje.value = f"❌ Error al cargar foto: {str(ex)}"
                mensaje.color = "red"
                page.update()
    
    file_picker = ft.FilePicker(on_result=seleccionar_foto)
    page.overlay.append(file_picker)
    
    def registrar_empresa(e):
        # Validar campos
        if not all([nombre_field.value, servicio_field.value, telefono_field.value, 
                   direccion_field.value, detalles_field.value]):
            mensaje.value = "❌ Por favor complete todos los campos"
            mensaje.color = "red"
            page.update()
            return
        
        if empresa_editando[0]:
            # Modo edición
            empresa_editando[0].nombre = nombre_field.value
            empresa_editando[0].servicio = servicio_field.value
            empresa_editando[0].telefono = telefono_field.value
            empresa_editando[0].direccion = direccion_field.value
            empresa_editando[0].detalles = detalles_field.value
            if foto_seleccionada[0]:
                empresa_editando[0].foto = foto_seleccionada[0]
            
            mensaje.value = f"✅ Empresa '{empresa_editando[0].nombre}' actualizada"
        else:
            # Modo creación
            empresa = Empresa(
                nombre_field.value,
                servicio_field.value,
                telefono_field.value,
                direccion_field.value,
                detalles_field.value,
                foto_seleccionada[0]
            )
            inventario.append(empresa)
            mensaje.value = f"✅ Empresa '{empresa.nombre}' registrada correctamente"
        
        # Guardar en archivo
        AlmacenamientoEmpresas.guardar(inventario)
        
        mensaje.color = "green"
        limpiar_campos()
        page.update()
    
    def editar_empresa(empresa):
        empresa_editando[0] = empresa
        nombre_field.value = empresa.nombre
        servicio_field.value = empresa.servicio
        telefono_field.value = empresa.telefono
        direccion_field.value = empresa.direccion
        detalles_field.value = empresa.detalles
        
        if empresa.foto:
            foto_seleccionada[0] = empresa.foto
            imagen_preview.src_base64 = empresa.foto
            imagen_preview.visible = True
        
        mostrar_menu_principal()
        mensaje.value = f"✏️ Editando: {empresa.nombre}"
        mensaje.color = "blue"
        page.update()
    
    def confirmar_eliminar(empresa):
        def eliminar(e):
            try:
                empresa_a_borrar = None
                for emp in inventario:
                    if emp.id == empresa.id:
                        empresa_a_borrar = emp
                        break
                
                if empresa_a_borrar:
                    inventario.remove(empresa_a_borrar)
                    AlmacenamientoEmpresas.guardar(inventario)

                    # Cerrar diálogo correctamente
                    page.dialog.open = False
                    page.update()

                    # Mostrar mensaje de éxito visual (SnackBar)
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f" Empresa '{empresa.nombre}' eliminada"),
                        bgcolor="green"
                    )
                    page.snack_bar.open = True

                    # Recargar la lista
                    mostrar_inventario(None)
                else:
                    # Si llegamos aaquí, no se encontró la empresa
                    print("Error: Empresa no encontrada para eliminar.")

            except Exception as ex:
                # Mostrar mensaje de error visual (SnackBar)
                print(f"Error al eliminar: {ex}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error al eliminar: {str(ex)}"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()

        def cancelar(e):
            page.dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar eliminación"),
            content=ft.Text(f"¿Está seguro de eliminar la empresa '{empresa.nombre}'? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton(
                    "Eliminar",
                    on_click=eliminar,
                    style=ft.ButtonStyle(color="red")
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def crear_card_empresa(i, empresa):
        foto_widget = ft.Container()
        if empresa.foto:
            foto_widget = ft.Image(
                src_base64=empresa.foto,
                width=100,
                height=100,
                fit=ft.ImageFit.COVER,
                border_radius=10
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Empresa #{i}", weight="bold", size=16),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, emp=empresa: editar_empresa(emp)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color="red",
                                on_click=lambda e, emp=empresa: confirmar_eliminar(emp)
                            ),
                        ]),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Row([
                        foto_widget,
                        ft.Column([
                            ft.Text(f"📌 {empresa.nombre}", weight="bold", size=14),
                            ft.Text(f"🔧 {empresa.servicio}"),
                            ft.Text(f"📞 {empresa.telefono}"),
                            ft.Text(f"📍 {empresa.direccion}"),
                        ], spacing=5),
                    ], spacing=15),
                    ft.Text(f"💬 {empresa.detalles}", italic=True, size=12),
                    ft.Text(f"📅 Registrado: {empresa.fecha_registro}", size=10, color="grey"),
                ], spacing=10),
                padding=15,
            ),
            elevation=2,
        )
    
    def buscar_empresas(query):
        lista_empresas.controls.clear()
        query = query.lower().strip()
        
        empresas_filtradas = [
            emp for emp in inventario
            if query in emp.nombre.lower() or query in emp.servicio.lower()
        ] if query else inventario
        
        if not empresas_filtradas:
            lista_empresas.controls.append(
                ft.Text("No se encontraron empresas", italic=True, color="grey")
            )
        else:
            for i, empresa in enumerate(empresas_filtradas, start=1):
                lista_empresas.controls.append(crear_card_empresa(i, empresa))
        
        page.update()
    
    def mostrar_inventario(e):
        lista_empresas.controls.clear()
        busqueda_field.value = ""
        
        if not inventario:
            lista_empresas.controls.append(
                ft.Text("No hay empresas registradas", italic=True, color="grey")
            )
        else:
            for i, empresa in enumerate(inventario, start=1):
                lista_empresas.controls.append(crear_card_empresa(i, empresa))
        
        page.controls.clear()
        page.add(
            ft.AppBar(
                title=ft.Text("Inventario de Empresas"),
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=volver_menu),
                actions=[
                    ft.IconButton(icon=ft.Icons.DOWNLOAD, tooltip="Exportar", on_click=exportar_datos)
                ],
            ),
            busqueda_field,
            ft.Container(height=10),
            lista_empresas,
        )
        page.update()
    
    def exportar_datos(e):
        filename = AlmacenamientoEmpresas.exportar_txt(inventario)
        if filename:
            dialog = ft.AlertDialog(
                title=ft.Text("✅ Exportación exitosa"),
                content=ft.Text(f"Archivo guardado como:\n{filename}"),
                actions=[ft.TextButton("OK", on_click=lambda e: cerrar_dialog())],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
    
    def cerrar_dialog():
        page.dialog.open = False
        page.update()
    
    def volver_menu(e):
        limpiar_campos()
        mostrar_menu_principal()
    
    def mostrar_menu_principal():
        page.controls.clear()
        
        boton_texto = "Actualizar Empresa" if empresa_editando[0] else "Registrar Empresa"
        boton_icono = ft.Icons.UPDATE if empresa_editando[0] else ft.Icons.ADD_BUSINESS
        
        page.add(
            ft.AppBar(title=ft.Text("Registro de Empresas Pro")),
            ft.Container(height=20),
            ft.Text("Datos de la Empresa", size=24, weight="bold"),
            ft.Container(height=10),
            nombre_field,
            servicio_field,
            telefono_field,
            direccion_field,
            detalles_field,
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton(
                    "Seleccionar Foto",
                    icon=ft.Icons.PHOTO_CAMERA,
                    on_click=lambda _: file_picker.pick_files(
                        allowed_extensions=["jpg", "jpeg", "png"],
                        allow_multiple=False
                    )
                ),
            ]),
            imagen_preview,
            ft.Container(height=10),
            mensaje,
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton(
                    boton_texto,
                    icon=boton_icono,
                    on_click=registrar_empresa,
                ),
                ft.ElevatedButton(
                    "Ver Inventario",
                    icon=ft.Icons.LIST,
                    on_click=mostrar_inventario,
                ),
            ], spacing=10),
            ft.Container(height=20),
            ft.Text(f"📊 Total de empresas: {len(inventario)}", size=16, weight="bold"),
        )
        page.update()
    
    # Mostrar menú principal al inicio
    mostrar_menu_principal()

if __name__ == "__main__":
    ft.app(target=main)