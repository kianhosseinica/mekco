function loadSubcategories(categoryId) {
    const subcategorySelect = document.getElementById('id_subcategory');

    fetch(`/ecommerce/load-subcategories/?category_id=${categoryId}`)
        .then(response => response.json())
        .then(data => {
            subcategorySelect.innerHTML = '<option value="">Select a subcategory</option>';
            data.subcategories.forEach(subcategory => {
                subcategorySelect.innerHTML += `<option value="${subcategory.id}">${subcategory.name}</option>`;
            });
            loadItems(categoryId);
        });
}

function loadItems(categoryId) {
    const itemsContainer = document.getElementById('items-container');

    fetch(`/ecommerce/load-items/?category_id=${categoryId}`)
        .then(response => response.json())
        .then(data => {
            itemsContainer.innerHTML = '';
            data.items.forEach(item => {
                itemsContainer.innerHTML += `<p>${item.description} - ${item.manufacturer_sku} - ${item.system_sku} - ${item.price_default}</p>`;
            });
        });
}
