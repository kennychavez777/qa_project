$('.process-select').change(function () {
    let processId = $(this).val();
    let processData = { id: processId };
    $('.user-select')
        .find('option')
        .remove()
        .end();
    $('.user-select').append(`<option selected>Seleccione un usuario</option>`);

    $.ajax({
        type: "POST",
        contentType: 'application/json',
        url: '/get-usuarios',
        dataType: 'json',
        data: JSON.stringify(processData),
        success: function(data){
            data.forEach(item => {
                $('.user-select').append(`<option value="${item[0]}">${item[1]}</option>`);
            });
        },
    });
});