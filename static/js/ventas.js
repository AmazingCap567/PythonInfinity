document.addEventListener("DOMContentLoaded", function () {
    // ===========================
    // 1. Actualizar precio producto
    // ===========================
    const selectProducto = document.querySelector("select[name='id_producto']");
    const precioInput = document.getElementById("precio");

    if (selectProducto && precioInput) {
        selectProducto.addEventListener("change", actualizarPrecio);
        actualizarPrecio();
    }

    function actualizarPrecio() {
        const selected = selectProducto.options[selectProducto.selectedIndex];
        if (selected) {
            precioInput.value = selected.getAttribute("data-precio") || "";
        }
    }

    // ================================
    // 2. Bloquear campos si cliente confirmado
    // ================================
    const flagElement = document.getElementById("cliente_confirmado_flag");
    const clienteConfirmado = flagElement && flagElement.value === "1";

    if (clienteConfirmado) {
        ["nombre", "apellidos", "correo", "direccion", "ruc", "razon_social", "cod_cliente"].forEach(id => {
            const campo = document.getElementById(id);
            if (campo) {
                campo.disabled = true;
                campo.style.backgroundColor = "transparent";
                campo.style.border = "none";
            }
        });
    }

    // ============================
    // 3. Búsqueda de cliente en modal
    // ============================
    const inputBusqueda = document.getElementById("busqueda");
    const resultadosLista = document.getElementById("resultados");

    if (inputBusqueda && resultadosLista) {
        inputBusqueda.addEventListener("input", function () {
            const query = this.value.trim();
            resultadosLista.innerHTML = "";

            if (!query) return;

            fetch("/vendedor/buscar_cliente", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `termino=${encodeURIComponent(query)}`
            })
            .then(response => response.json())
            .then(clientes => {
                clientes.forEach(cliente => {
                    const li = document.createElement("li");
                    li.textContent = `${cliente.nombre} ${cliente.apellidos} - ${cliente.ruc}`;
                    li.onclick = function () {
                        document.getElementById("cod_cliente").value = cliente.id_cliente || "";
                        document.getElementById("nombre").value = cliente.nombre || "";
                        document.getElementById("apellidos").value = cliente.apellidos || "";
                        document.getElementById("correo").value = cliente.correo || "";
                        document.getElementById("direccion").value = cliente.direccion || "";
                        document.getElementById("ruc").value = cliente.ruc || "";
                        document.getElementById("razon_social").value = cliente.razon_social || "";
                        cerrarModal();
                    };
                    resultadosLista.appendChild(li);
                });
            })
            .catch(error => {
                console.error("Error en la búsqueda:", error);
            });
        });
    }

    // ======================
    // 4. Funciones auxiliares
    // ======================
    window.mostrarModal = function () {
        const modal = document.getElementById("modal");
        if (modal) modal.style.display = "block";
    };

    window.cerrarModal = function () {
        const modal = document.getElementById("modal");
        if (modal) modal.style.display = "none";
    };

    window.habilitarCampos = function () {
        ["nombre", "apellidos", "correo", "direccion", "ruc", "razon_social", "cod_cliente"].forEach(id => {
            const campo = document.getElementById(id);
            if (campo) {
                campo.disabled = false;
                campo.style.backgroundColor = ""; // restaura fondo
                campo.style.border = ""; // restaura borde
            }
        });

        const div = document.getElementById("cliente-seleccionado");
        if (div) div.style.display = "none";
    };
});
