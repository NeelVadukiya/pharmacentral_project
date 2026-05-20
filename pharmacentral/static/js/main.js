document.addEventListener('DOMContentLoaded', function () {
  // Date in header
  var el = document.getElementById('headerDate');
  if (el) el.textContent = new Date().toDateString();

  // Default sale date to today
  var saleDateField = document.getElementById('saleDateField');
  if (saleDateField && !saleDateField.value)
    saleDateField.value = new Date().toISOString().split('T')[0];

  // Init sale form
  if (document.getElementById('saleItemsContainer') !== null)
    addSaleRow();

  // Auto-hide flash messages
  document.querySelectorAll('.flash-msg').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 500);
    }, 4000);
  });
});

// ── Sale rows ──────────────────────────────────────────────────────────────
var saleRowCount = 0;

function drugOptions() {
  if (typeof DRUGS === 'undefined') return '';
  return '<option value="">-- Select Drug --</option>' +
    DRUGS.map(function (d) {
      return '<option value="' + d.id + '">' +
        d.name + ' (Rs.' + d.price.toFixed(2) + ') [Stock: ' + d.stock + ']</option>';
    }).join('');
}

function addSaleRow() {
  var c = saleRowCount++;
  var container = document.getElementById('saleItemsContainer');
  if (!container) return;
  var row = document.createElement('div');
  row.className = 'sale-item-row';
  row.id = 'saleRow' + c;
  row.innerHTML =
    '<div class="form-group" style="flex:2;min-width:160px">' +
      '<select name="drug_id[]" id="sDrug' + c + '" class="form-control" onchange="fillSalePrice(' + c + ')">' +
        drugOptions() +
      '</select>' +
    '</div>' +
    '<div class="form-group" style="min-width:70px">' +
      '<label style="font-size:0.72rem">Qty</label>' +
      '<input type="number" name="quantity[]" id="sQty' + c + '" class="form-control" value="1" min="1" oninput="calcSaleTotal()">' +
    '</div>' +
    '<div class="form-group" style="min-width:80px">' +
      '<label style="font-size:0.72rem">Price Rs.</label>' +
      '<input type="number" name="price[]" id="sPrice' + c + '" class="form-control" placeholder="0.00" min="0" step="0.01" oninput="calcSaleTotal()">' +
    '</div>' +
    '<button type="button" class="btn btn-red btn-sm" onclick="removeSaleRow(' + c + ')" style="margin-bottom:2px">✕</button>';
  container.appendChild(row);
}

function removeSaleRow(c) {
  var el = document.getElementById('saleRow' + c);
  if (el) { el.remove(); calcSaleTotal(); }
}

function fillSalePrice(c) {
  var sel = document.getElementById('sDrug' + c);
  if (!sel || !sel.value) return;
  var drug = DRUGS.find(function (d) { return d.id === parseInt(sel.value); });
  if (drug) {
    document.getElementById('sPrice' + c).value = drug.price.toFixed(2);
    calcSaleTotal();
  }
}

function calcSaleTotal() {
  var total = 0;
  document.querySelectorAll('.sale-item-row').forEach(function (row) {
    var id = row.id.replace('saleRow', '');
    var q  = parseFloat(document.getElementById('sQty'   + id)?.value) || 0;
    var p  = parseFloat(document.getElementById('sPrice' + id)?.value) || 0;
    total += q * p;
  });
  var el = document.getElementById('saleGrandTotal');
  if (el) el.textContent = total.toFixed(2);
}

// Sale form validation
var saleForm = document.getElementById('saleForm');
if (saleForm) {
  saleForm.addEventListener('submit', function (e) {
    var hasItem = false;
    document.querySelectorAll('.sale-item-row').forEach(function (row) {
      var id  = row.id.replace('saleRow', '');
      var sel = document.getElementById('sDrug' + id);
      if (sel && sel.value) hasItem = true;
    });
    if (!hasItem) {
      e.preventDefault();
      alert('Please add at least one item to the sale.');
    }
  });
}

// ── Print bill ─────────────────────────────────────────────────────────────
function printBill() { window.print(); }
