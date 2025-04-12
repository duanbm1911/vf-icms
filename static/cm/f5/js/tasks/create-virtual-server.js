$(document).ready(function () {
  var initData = [["","","","","","","","","","",""]];
  var container = document.getElementById('dataTable');
  var hot = new Handsontable(container, {
    data: initData,
    rowHeaders: true,
    colWidths: 250,
    rowHeights: 100,
    height: 400,
    colHeaders: [
      'F5 device (required)', 
      'Service name (required)', 
      'Virtual server IP (required)', 
      'Pool member (required)', 
      'Pool monitor (required)',
      'Pool LB method (required)',
      'Client SSL profile', 
      'Server SSL profile', 
      'Irule profile', 
      'WAF profile', 
      'F5 template (required)'
    ],
    manualColumnResize: true,
    columns: [
      {
        type: 'autocomplete',
        source(query, process) {
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/device',
            success: function (response) {
              process(response.datalist)
            }
          })
        },
        strict: true,
        allowInvalid: false
      }, {}, {}, {}, 
      {
        type: 'autocomplete',
        strict: true,
        allowInvalid: false,
        source(query, process) {
          let row = this.row
          let f5_device_ip = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/pool-monitor?f5_device_ip=' + f5_device_ip,
            success: function (response) {
              process(response.datalist)
            }
          })
        }
      },
      {
        type: 'autocomplete',
        strict: true,
        allowInvalid: false,
        source(query, process) {
          let row = this.row
          let f5_device_ip = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/pool-lb-method?f5_device_ip=' + f5_device_ip,
            success: function (response) {
              process(response.datalist)
            }
          })
        }
      },
      {
        type: 'autocomplete',
        allowInvalid: false,
        source(query, process) {
          let row = this.row
          let f5_device_ip = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/client-ssl-profile?f5_device_ip=' + f5_device_ip,
            success: function (response) {
              process(response.datalist)
            }
          })
        },
      },
      {
        type: 'autocomplete',
        allowInvalid: false,
        source(query, process) {
          let row = this.row
          let f5_device_ip = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/server-ssl-profile?f5_device_ip=' + f5_device_ip,
            success: function (response) {
              process(response.datalist)
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
        type: 'autocomplete',
        allowInvalid: false,
        source(query, process) {
          let row = this.row
          let f5_device_ip = hot.getDataAtCell(row, 0)
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/waf-profile?f5_device_ip=' + f5_device_ip,
            success: function (response) {
              process(response.datalist)
            }
          })
        }
      },
      {
        type: 'autocomplete',
        strict: true,
        allowInvalid: false,
        allowEmpty: false,
        source(query, process) {
          $.ajax({
            type: "GET",
            url: '/api/cm/f5/get/template',
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
    var f5_device_ip = instance.getDataAtRow(row)[0]
    $.ajax({
      type: "GET",
      url: '/api/cm/f5/get/irule-profile?f5_device_ip=' + f5_device_ip,
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
    console.log(datalist);
    $.ajax({
      type: "POST",
      url: '/api/cm/f5/task/create/virtual-server',
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
            window.location = '/cm/f5/tasks/list';
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

