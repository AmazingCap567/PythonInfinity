document.addEventListener("DOMContentLoaded", function () {
    // ===========================
    // 1. Actualizar precio producto y stock
    // ===========================
    const selectProducto = document.getElementById("id_producto");
    const precioInput = document.getElementById("precio");
    const cantidadInput = document.querySelector("input[name='cantidad']");
    const stockInput = document.getElementById("stock_disponible");  // ✅ corregido
    const btnAgregar = document.querySelector("form[action*='agregar_producto'] button[type='submit']");
    btnAgregar.id = "btn-agregar";

    const advertencia = document.getElementById("advertencia-stock");

    function actualizarPrecioYStock() {
        const selected = selectProducto.options[selectProducto.selectedIndex];
        if (selected) {
            precioInput.value = selected.getAttribute("data-precio") || "";
            stockInput.value = selected.getAttribute("data-stock") || "0";
            validarCantidad();
        }
    }

    function validarCantidad() {
        const cantidad = parseInt(cantidadInput.value) || 0;
        const stock = parseInt(stockInput.value) || 0;

        if (cantidad > stock) {
            btnAgregar.disabled = true;
            advertencia.textContent = "Cantidad supera el stock disponible.";
        } else {
            btnAgregar.disabled = false;
            advertencia.textContent = "";
        }
    }

    if (selectProducto && precioInput && cantidadInput && stockInput && advertencia) {
        selectProducto.addEventListener("change", actualizarPrecioYStock);
        cantidadInput.addEventListener("input", validarCantidad);
        actualizarPrecioYStock(); // inicial
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
                campo.style.backgroundColor = "";
                campo.style.border = "";
            }
        });

        const div = document.getElementById("cliente-seleccionado");
        if (div) div.style.display = "none";
    };
});
