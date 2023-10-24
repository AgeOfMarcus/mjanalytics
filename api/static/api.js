function api(route, data, callback) {
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "https://analytics.marcusj.org/api" + route,
        data: JSON.stringify(data),
        success: callback,
        dataType: "json"
    })
}