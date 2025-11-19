// Load graph
async function loadGraph() {
    const response = await fetch("/graph");
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    const img = document.getElementById("plot");
    if (img.src.startsWith("blob:")) {
        URL.revokeObjectURL(img.src);
    }
    img.src = url;
}

// Load table
async function loadTable() {
    const response = await fetch("/table");
    const data = await response.json();

    const table = document.getElementById("table");
    table.innerHTML = "";

    if (data.length === 0) return;

    const header = table.createTHead();
    const headerRow = header.insertRow();
    Object.keys(data[0]).forEach(key => {
        const th = document.createElement("th");
        th.innerText = key;
        headerRow.appendChild(th);
    });

    const tbody = table.createTBody();
    data.forEach(rowData => {
        const row = tbody.insertRow();
        Object.values(rowData).forEach(val => {
            const cell = row.insertCell();
            cell.innerText = val;
        });
    });
}

// Attach event listeners
document.getElementById("btnGraph").addEventListener("click", loadGraph);
document.getElementById("btnTable").addEventListener("click", loadTable);
