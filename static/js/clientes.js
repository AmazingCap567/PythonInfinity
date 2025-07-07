document.addEventListener("DOMContentLoaded", function () {
    const buscador = document.getElementById("buscador");
    const tablaBody = document.getElementById("tabla-body");

    function limpiarCampo(valor) {
        return valor === null || valor === undefined ? "" : valor;
    }

    function buscarClientes(termino) {
        fetch("/vendedor/api/buscar_clientes", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `termino=${encodeURIComponent(termino)}`
        })
        .then(response => response.json())
        .then(data => {
            tablaBody.innerHTML = "";
            if (data.length === 0) {
                tablaBody.innerHTML = `<tr><td colspan="8">No se encontraron clientes</td></tr>`;
            } else {
                data.forEach(c => {
                    const fila = `
                        <tr>
                            <td>${limpiarCampo(c.id_cliente)}</td>
                            <td>${limpiarCampo(c.nombre)}</td>
                            <td>${limpiarCampo(c.apellidos)}</td>
                            <td>${limpiarCampo(c.ruc)}</td>
                            <td>${limpiarCampo(c.razon_social)}</td>
                            <td>${limpiarCampo(c.correo)}</td>
                            <td>${limpiarCampo(c.telefono)}</td>
                            <td>${limpiarCampo(c.direccion)}</td>
                        </tr>
                    `;
                    tablaBody.insertAdjacentHTML("beforeend", fila);
                });
            }
        })
        .catch(err => {
            console.error("Error al buscar clientes:", err);
            tablaBody.innerHTML = `<tr><td colspan="8">Error al cargar datos</td></tr>`;
        });
    }

    buscador.addEventListener("input", () => {
        buscarClientes(buscador.value);
    });

    buscarClientes("");
});
