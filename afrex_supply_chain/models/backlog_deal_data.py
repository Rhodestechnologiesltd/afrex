from odoo import models, fields, api, _


class Backlog(models.Model):
    _name = 'asc.backlog'
    _description = 'Migrated data'
    _rec_name = 'trade_folder'

    trade_folder = fields.Char(string="Trade Folder")
    supplier = fields.Char(string="Supplier / Shipper")
    buyer = fields.Char(string="Buyer")
    consignee_notify = fields.Char(string="Consignee / Notify Party")

    # Buyer PO
    buyer_po_number = fields.Char(string="Buyer PO Number")
    buyer_po_date = fields.Date(string="Buyer PO Date")

    # Supplier
    afrex_po_number = fields.Char(string="Afrex PO Number")
    supplier_pfi_date = fields.Date(string="Supplier PFI Date")
    supplier_pfi_ref = fields.Char(string="Supplier PFI No / Ref")

    # Product & Pricing
    product = fields.Char(string="Product")
    mt_ordered = fields.Float(string="MT Ordered")
    currency_code = fields.Char(string="Currency Code")
    price_per_ton = fields.Float(string="Price per Ton (CIF / CFR / FOB)")
    supplier_invoice_amount = fields.Float(string="Supplier Invoice Amount")

    # Payment – Supplier
    advance_payment_percent = fields.Float(string="Advance Payment (%)")
    final_payment_percent = fields.Float(string="Final Payment (%)")
    advance_amount = fields.Float(string="Advance Amount")
    advance_payment_concluded = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Advance Payment Concluded"
    )
    advance_payment_date = fields.Date(string="Advance Payment Date")
    final_amount_usd = fields.Float(string="Final Amount (USD)")
    final_payment_concluded = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Final Payment Concluded"
    )
    final_payment_date = fields.Date(string="Final Payment Date")

    # Logistics
    container_count = fields.Integer(string="Container Count")
    container_size_type = fields.Char(string="Container Size and Type")
    packaging = fields.Char(string="Packaging")
    origin = fields.Char(string="Origin")
    port_of_loading = fields.Char(string="Port of Loading")
    shipper_incoterms = fields.Char(string="Shipper's Incoterms")
    port_of_discharge = fields.Char(string="Port of Discharge")
    carrier_shipping_line = fields.Char(string="Carrier / Shipping Line")
    forwarder = fields.Char(string="Forwarder")
    bl_booking_no = fields.Char(string="BL / Booking No")
    vessel_voyage = fields.Char(string="Vessel Name / Voyage No")
    container_no = fields.Char(string="Container No")
    seal_no = fields.Char(string="Seal No")

    expected_shipment_date = fields.Date(string="Expected Shipment Date (Supplier PFI)")
    actual_expected_shipment_date = fields.Date(string="Actual / Expected Shipment Date")
    shipment_default = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Shipment Default"
    )

    eta_arrival_date = fields.Date(string="ETA – Arrival POD")
    actual_arrival_pod = fields.Date(string="Actual Arrival POD")

    comment_status = fields.Text(string="Comment / Status")

    # Shipping Documents
    shipper_docs = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Shipper Docs"
    )
    shipper_docs_date = fields.Date(string="Shipper Docs Date")
    bl_release = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="BL Release"
    )
    bl_release_date = fields.Date(string="BL Release Date")

    # Invoicing – Afrex
    proforma_invoice_raised = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Afrex Proforma Invoice Raised"
    )
    proforma_invoice_date = fields.Date(string="Proforma Invoice Date")

    commercial_invoice_raised = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Afrex Commercial Invoice Raised"
    )
    commercial_invoice_date = fields.Date(string="Commercial Invoice Date")
    afrex_invoice_number = fields.Char(string="Afrex Invoice Number")

    # Buyer Payment
    buyer_payment_terms = fields.Char(string="Buyer Payment Terms")
    selling_price_per_ton_usd = fields.Float(string="Selling Price per Ton (USD)")
    buyer_incoterms = fields.Char(string="Buyer Incoterms")
    amount_usd = fields.Float(string="Amount USD")
    amount_zar = fields.Float(string="Amount ZAR")
    payment_due_date = fields.Date(string="Payment Due Date")
    buyer_paid = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Has Buyer Paid"
    )
    buyer_actual_payment_date = fields.Date(string="Buyer Actual Payment Date")

    # Deal Status
    deal_status_logistics = fields.Selection(
        [('active', 'Active'), ('close', 'Closed')],
        string="Deal Status: Logistics"
    )
    eazzy_filed = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="EAZZY Filed"
    )
    deal_status_accounting = fields.Selection(
        [('active', 'Active'), ('close', 'Closed')],
        string="Deal Status: Logistics"
    )

    # Supplier Costing
    supplier_payment_terms = fields.Char(string="Supplier Payment Terms")
    no_of_packages = fields.Integer(string="No. of Packages")
    gross_weight_kgs = fields.Float(string="Gross Weight (KGS)")
    supplier_fob_usd = fields.Float(string="Supplier FOB (USD)")
    supplier_freight_usd = fields.Float(string="Supplier Freight (USD)")
    supplier_insurance_usd = fields.Float(string="Supplier Insurance (USD)")
    afrex_fob_usd = fields.Float(string="Afrex FOB (USD)")

    product_specification = fields.Text(string="Product Specification")
    supplier_commercial_invoice_no = fields.Char(string="Supplier Commercial Invoice Number")
    subject_to_switch = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Subject to Switch"
    )
    switch_invoice_no = fields.Char(string="Switch Invoice No")
    switch_amount = fields.Float(string="Switch Amount")
    tariff_code = fields.Char(string="Tariff Code")
    mt_delivered = fields.Float(string="MT Delivered")
