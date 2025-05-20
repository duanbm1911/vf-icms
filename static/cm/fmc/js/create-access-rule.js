$(document).ready(function () {
  var initData = [["", "", "", "", "", "", "", "", "", ""]];
  var container = document.getElementById('dataTable');
  var hot = new Handsontable(container, {
    data: initData,
    rowHeaders: true,
    colWidths: '100%',
    rowHeights: 100,
    stretchH: 'all',
    colHeaders: [
      'Site',
      'Domain',
      'Policy',
      'Gateway',
      'Name',
      'Source',
      'Destination',
      'Protocol',
      'Schedule',
      'Section'
    ],
    manualColumnResize: true,
    columns: [
      {
        type: 'autocomplete',
        source(query, process) {
          $.ajax({
            type: "GET",
            url: '/api/cm/fmc/site',
            success: function (response) {
              process(response.datalist)
            }
          })
        },
        strict: false,
        allowInvalid: false
      },
      {
        type: 'autocomplete',
        source(query, process) {
          let row = this.row
          let site = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/fmc/domain?site=' + site,
            url: '/api/cm/fmc/site',
            success: function (response) {
              process(response.datalist)
            }
          })
        },
        strict: false,
        allowInvalid: false
      },
      {
        type: 'autocomplete',
        source(query, process) {
          let row = this.row
          let site = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/fmc/domain?site=' + site,
            success: function (response) {
              process(response.datalist)
            }
          })
        },
        strict: false,
        allowInvalid: false
      },
      {
        type: 'autocomplete',
        source(query, process) {
          let row = this.row
          let site = hot.getDataAtCell(row, 0)
          let domain = hot.getDataAtCell(row, 1)
          $.ajax({
            type: "GET",
            url: '/api/cm/fmc/policy?domain=' + domain + '&site=' + site,
            success: function (response) {
              process(response.data)
            }
          })
        },
        strict: false,
        allowInvalid: false
      },
      {
        renderer: customDropdownRenderer,
        editor: "chosen",
        chosenOptions: {
          multiple: true,
          data: []
        }
      }, {}, {}, {}, {},
      {
        type: 'date',
        dateFormat: 'YYYY-MM-DD',
        correctFormat: true,
        datePickerConfig: {
          firstDay: 0,
          showWeekNumber: true,
          numberOfMonths: 1
        },
        strict: false,
        allowInvalid: true
      },
      {
        type: 'autocomplete',
        strict: false,
        allowInvalid: false,
        source(query, process) {
          let row = this.row
          let policy = hot.getDataAtCell(row, 2)
          let policy = hot.getDataAtCell(row, 2)
          $.ajax({
            type: "GET",
            url: '/api/cm/fmc/category?policy=' + policy,
            success: function (response) {
              process(response.datalist)
            }
          })
        }
      }
    ],
    autoWrapRow: true,
    autoWrapCol: true
  });
  function customDropdownRenderer(instance, td, row, col, prop, value, cellProperties) {
    var selectedId;
    var policy = instance.getDataAtRow(row)[2]
    var policy = instance.getDataAtRow(row)[2]
    $.ajax({
      type: "GET",
      url: '/api/cm/fmc/gateway?policy=' + policy,
      success: function (response) {
        cellProperties.chosenOptions.data = response.datalist
      }
    })
    var optionsList = cellProperties.chosenOptions.data;
    if (typeof optionsList === "undefined" || typeof optionsList.length === "undefined" || optionsList.length === 0 || !optionsList.length) {
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
    console.log(datalist);
    $.ajax({
      type: "POST",
      url: '/api/cm/fmc/create-rule',
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
            window.location = '/cm/fmc/access-rule/list';
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

