$(document).ready(function () {
  var initData = [["","","","",""]];
  var container = document.getElementById('dataTable');
  var hot = new Handsontable(container, {
    data: initData,
    rowHeaders: true,
    colWidths: '100%',
    rowHeights: 100,
    stretchH: 'all',
    colHeaders: [
      'Site', 
      'Policy', 
      'User', 
      'Expiration data', 
      'Note'
    ],
    manualColumnResize: true,
    columns: [
      {
        type: 'autocomplete',
        source(query, process) {
          $.ajax({
            type: "GET",
            url: '/api/cm/checkpoint/get-list-site',
            success: function (response) {
              let listSite = Array()
              for (i in response.datalist) {
                listSite.push(response.datalist[i].site)
              }
              process(listSite)
            }
          })
        },
        strict: true,
        allowInvalid: false
      },
      {
        type: 'autocomplete',
        strict: true,
        allowInvalid: true,
        source(query, process) {
          let row = this.row
          let site = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/checkpoint/get-list-policy?site=' + site,
            success: function (response) {
              process(response.data)
            }
          })
        }
      },
      {
        renderer: customDropdownRenderer,
        editor: "chosen",
        chosenOptions: {
          multiple: true,
          data: []
        }
      },
      {
        type: 'date',
        dateFormat: 'YYYY-MM-DD',
        correctFormat: true,
        datePickerConfig: {
          firstDay: 0,
          showWeekNumber: true,
          numberOfMonths: 1
        },
        strict: true,
        allowInvalid: true
      },
      {}
    ],
    autoWrapRow: true,
    autoWrapCol: true
  });
  function customDropdownRenderer(instance, td, row, col, prop, value, cellProperties) {
    var selectedId;
    var site = instance.getDataAtRow(row)[0]
    $.ajax({
      type: "GET",
      url: '/api/cm/checkpoint/get-list-local-user?site=' + site,
      success: function (response) {
        cellProperties.chosenOptions.data = response.datalist
      }
    })
    var optionsList = cellProperties.chosenOptions.data;
    if(typeof optionsList === "undefined" || typeof optionsList.length === "undefined" || optionsList.length === 0 || !optionsList.length) {
      Handsontable.cellTypes.text.renderer(instance, td, row, col, prop, value, cellProperties);
      return td;
    }

    var values = (value + "").split(",");
    value = [];
    for (var index = 0; index < optionsList.length; index++) {

        if (values.indexOf(optionsList[index].id + "") > -1) {
            selectedId = optionsList[index].id;
            value.push(optionsList[index].label);
        }
    }
    value = value.join(", ");
    Handsontable.cellTypes.text.renderer(instance, td, row, col, prop, value, cellProperties);
    return td;
  };

  document.querySelector('#add').addEventListener('click', function () {
    var col = hot.countRows();
    hot.alter('insert_row', col, 1)
  })
  document.querySelector('#submit').addEventListener('click', function () {
    $('#submit').prop('disabled', true)
    let datalist = hot.getData()
    $.ajax({
      type: "POST",
      url: '/api/cm/checkpoint/update-local-user',
      dataType: "json",
      data: {
        'datalist': datalist
      },
      success: function (response) {
        if (response.status == 'success') {
          Swal.fire({
            text: response.message,
            icon: "success"
          }).then(function () {
            window.location = '#';
          })
        }
        else {
          Swal.fire({
            text: response.message,
            icon: "error"
          }).then(function () {
            $('#submit').prop('disabled', false)
          })
        }
      },
      error: function (response) {
        Swal.fire({
          text: response.responseJSON.message,
          icon: "error"
        }).then(function () {
          $('#submit').text('Submit');
          $('#submit').prop('disabled', false)
        })
      }
    })
  })
})

