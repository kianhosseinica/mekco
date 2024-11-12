function setShippingCost(rateCost, serviceName) {
    document.getElementById('manual_shipping_cost').value = rateCost.toFixed(2);
    document.getElementById('shipping_service_name').value = serviceName;
    console.log(`Selected shipping cost: ${rateCost}, Service: ${serviceName}`);
}
