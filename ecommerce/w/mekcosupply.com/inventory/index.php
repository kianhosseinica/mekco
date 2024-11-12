<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: #2c3e50;
        }

        .summary {
            display: flex;
            justify-content: space-between;
            padding: 20px;
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .summary div {
            font-size: 18px;
            margin-bottom: 10px;
            flex-basis: 100%;
        }

        @media (min-width: 768px) {
            .summary div {
                flex-basis: auto;
            }
        }

        .table-container {
            overflow-x: auto;
            background-color: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 600px; /* Ensures table remains scrollable if it exceeds screen width */
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
            white-space: nowrap; /* Prevents text from wrapping */
        }

        th {
            background-color: #3498db;
            color: white;
            cursor: pointer;
        }

        tr:nth-child(even) {
            background-color: #f2f2f2;
        }

        .update-btn {
            padding: 8px 12px;
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .update-btn:hover {
            background-color: #2ecc71;
        }

        @media (max-width: 768px) {
            .table-container {
                padding: 5px;
            }

            th, td {
                padding: 8px;
                font-size: 14px;
            }

            .summary div {
                font-size: 16px;
            }
        }
    </style>
    <script>
        function sortTable(n) {
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.getElementById("inventoryTable");
            switching = true;
            dir = "asc"; 
            while (switching) {
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    if (dir == "asc") {
                        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (dir == "desc") {
                        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                } else {
                    if (switchcount == 0 && dir == "asc") {
                        dir = "desc";
                        switching = true;
                    }
                }
            }
        }
    </script>
</head>
<body>

<div class="container">
    <h1>Inventory Report</h1>

    <div class="summary">
        <div>Total Items in Stock: <span id="totalStock">0</span></div>
        <div>Total On Their Way: <span id="totalOnWay">0</span></div>
        <div>Number of Alerts: <span id="alertCount">0</span></div>
    </div>

    <div class="table-container">
        <table id="inventoryTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">#</th>
                    <th onclick="sortTable(1)">ITEM</th>
                    <th onclick="sortTable(2)">Stock</th>
                    <th onclick="sortTable(3)">Receiving</th>
                    <th onclick="sortTable(4)">Desired QTY</th>
                    <th onclick="sortTable(5)">Re-order Alert</th>
                    <th onclick="sortTable(5)">Re-order QTY</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Product A</td>
                    <td>50</td>
                    <td>30</td>
                    <td>10</td>
                    <td>15</td>
                    <td>15</td>
                    <td><button class="update-btn">Update</button></td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Product B</td>
                    <td>20</td>
                    <td>50</td>
                    <td>5</td>
                    <td>10</td>
                    <td>15</td>
                    <td><button class="update-btn">Update</button></td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Product C</td>
                    <td>50</td>
                    <td>30</td>
                    <td>10</td>
                    <td>15</td>
                    <td>15</td>
                    <td><button class="update-btn">Update</button></td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>Product D</td>
                    <td>20</td>
                    <td>50</td>
                    <td>5</td>
                    <td>10</td>
                    <td>15</td>
                    <td><button class="update-btn">Update</button></td>
                </tr>                
                <!-- Add more rows as needed -->
            </tbody>
        </table>
    </div>
</div>

</body>
</html>