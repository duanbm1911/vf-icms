$(document).ready(function () {
  var initData = [["", "", "", "", "", "", "", ""]];
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
            url: '/api/cm/fmc/policy?site=' + site,
            success: function (response) {
              process(response.data)
            }
          })
        },
        strict: false,
        allowInvalid: false
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
          let policy = hot.getDataAtCell(row, 1)
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

