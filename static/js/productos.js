// Modal de agregar/editar producto
function abrirModalNuevo() {
    document.getElementById("form-producto").reset();
    document.getElementById("id_producto").value = "";
    document.getElementById("modal-titulo").textContent = "Nuevo Producto";
    document.getElementById("modal-producto").style.display = "block";
}

function abrirEditarProducto(producto) {
    document.getElementById("id_producto").value = producto.id_producto;
    document.getElementById("nombre").value = producto.nombre || "";
    document.getElementById("descripcion").value = producto.descripcion || "";
    document.getElementById("tipo").value = producto.tipo || "";
    document.getElementById("precio").value = producto.precio;
    document.getElementById("stock").value = producto.stock;
    document.getElementById("color").value = producto.color || "";
    document.getElementById("material").value = producto.material || "";

    document.getElementById("modal-titulo").textContent = "Editar Producto";
    document.getElementById("modal-producto").style.display = "block";
}

function cerrarModal() {
    document.getElementById("modal-producto").style.display = "none";
}

// Eliminar producto: poner stock en 0
function eliminarProducto(id) {
    if (!confirm("¿Estás seguro de poner stock en 0 para este producto?")) return;
    fetch(`/gerente/productos/eliminar/${id}`, {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensaje);
        location.reload();
    });
}

// Guardar producto (nuevo o editado)
function guardarProducto(e) {
    e.preventDefault();

    const producto = {
        id_producto: document.getElementById("id_producto").value || null,
        nombre: document.getElementById("nombre").value,
        descripcion: document.getElementById("descripcion").value,
        tipo: document.getElementById("tipo").value,
        precio: parseFloat(document.getElementById("precio").value),
        stock: parseInt(document.getElementById("stock").value),
        color: document.getElementById("color").value,
        material: document.getElementById("material").value
    };

    const url = producto.id_producto ? "/gerente/editar_producto" : "/gerente/productos/agregar";

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(producto)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensaje);
        cerrarModal();
        location.reload();
    });
}

// Inicializar al cargar
document.addEventListener("DOMContentLoaded", function () {
    const formProducto = document.getElementById("form-producto");

    if (formProducto) {
        formProducto.addEventListener("submit", guardarProducto);
    }

    const btnLimpiar = document.getElementById("btn-limpiar");
    if (btnLimpiar) {
        btnLimpiar.addEventListener("click", function () {
            document.querySelector("form").reset();
            window.location.href = "/gerente/productos";  // recarga sin filtros
        });
    }
});
