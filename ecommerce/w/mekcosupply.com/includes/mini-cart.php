<!DOCTYPE html>
<html>
	<head>
		<title>Lightspeed Retail - Print</title>
		<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><meta name="apple-mobile-web-app-capable" content="yes">				<style>
		
@page { margin: 0px; }

body {
	font: normal 10pt 'Helvetica Neue', Helvetica, Arial, sans-serif black;
	width: auto;
	margin: 0 auto;
	padding: 0px; <!-- You need this to make the printer behave -->
	background-image: url("https://apprand.com/mekcosupply.com/img/Mekco-Tape-Design.jpg");
    background-repeat: repeat-x;

		}


.store {
	page-break-after: always;
}

.receipt {
	font: normal 10pt “Helvetica Neue”, Helvetica, Arial, sans-serif;
	color: #000;
}

h1 {
	margin: .5em 0 0;
	font-size: 12pt;
	text-align: center;
	color: #000;
}

p.date, p.copy {
	font-size: 9pt;
	margin: 0;
	text-align: center;
	color: #000;
}

p.details {
	font-size: 10pt;
	text-align: left;
	color: #000;
}

h2 {
	/*border-bottom: 1px solid black;*/
	text-transform: uppercase;
	font-size: 10pt;
	margin: .5em 0 0;
	color: #000;
}

.receiptHeader {
	text-align: center;
	color: #000;
}

.receiptHeader h3 {
	font-size: 12pt;
	margin: 0;
	color: #000;
}

.shipping h4 {
	margin-top: 0;
	color: #000;
}

.receiptHeader img {
	margin: 8px 0 4px;
	color: #000;
}

.receiptShopContact {
	margin: 0;
	color: #000;
}

table {
	margin: 0 0;
	width: 100%;
	border-collapse:collapse;
	color: #000;
}

table th { text-align: left; color: #000; }

table tbody th {
	font-weight: normal;
	text-align: left;
	color: #000;
}

table td.amount, table th.amount { text-align: right; color: #000;}
table td.quantity, table th.quantity { text-align: center; border-bottom: 1px dotted black; }

th.description {
	width: 100%;
	color: #000;
}

td.amount { white-space: nowrap; border-bottom: 1px dotted black; }

table.totals { text-align: right; }
table.payments { text-align: right; }
table.spacer { margin-top: 1em; }
table tr.total td { font-weight: bold; }

table td.amount { padding-left: 10px; }
table td.custom_field {
	padding-right: 10px;
	text-align: center;
}

table.sale { border-bottom: 1px solid black; }

table.sale th {
	border-bottom: 1px dotted black;
	font-weight: bold;
}

table div.line_description {
	text-align: left;
	font-weight: bold;
 border-bottom: 1px dotted black;
}

table div.line_note {
	text-align: left;
	padding-left: 10px;
}

table div.line_serial {
	text-align: left;
	font-weight: normal;
	padding-left: 10px;
}

table.workorders div.line_description {
	font-weight: normal;
	padding-left: 10px;
}

table.workorders div.line_note {
	font-weight: normal;
	padding-left: 10px;
}

table.workorders div.line_serial {
	font-weight: normal;
	padding-left: 20px;
}

table.workorders td.workorder div.line_note {
	font-weight: bold;
	padding-left: 0px;
}

p.thankyou {
	margin: 0;
	text-align: center;
	color: #000;
}

.note { text-align: center; color: #000; }


.barcodeContainer {
	margin-top: 15px;
	text-align: center;
	color: #000;
}

.workorders .barcodeContainer {
	margin-left: 15px;
	text-align: left;
}

dl {
	overflow: hidden
}

dl dt {
	font-weight: bold;
	width: 80px;
	float: left
}

dl dd {
	border-top: 2px solid black;
	padding-top: 2px;
	margin: 1em 0 0;
	float: left;
	width: 180px
}

dl dd p { margin: 0; }

.strike { text-decoration: line-through; }

.receiptCompanyNameField,
.receiptCustomerNameField,
.receiptCustomerVatField,
.receiptCustomerCompanyVatField,
.receiptCustomerAddressField,
.receiptPhonesContainer,
.receiptCustomerNoteField {
	display: block;
	color: #000;
}

table.payments td.label {
	font-weight: normal;
	text-align: right;
	width: 100%;
	color: #000;
}

#receiptTransactionDetails table {
	max-width: 245px;
	margin: 0 auto;
}

#receiptTransactionDetails table td {
	text-align: right;
}

#receiptTransactionDetails table td.top {
	font-weight: bold;
}

#receiptTransactionDetails table td.label {
	padding-right: 20px;
	text-align: left;
}


		</style>
			</head>
<body>
																																						
					<!-- replace.email_custom_header_msg -->
			<div>
					
					<div class="receiptHeader" style="color: #000;">
				
					<img src="https://res.cloudinary.com/lightspeed-retail/image/upload/w_225/esqiykxx7ajjhqkzdrbh.jpg" width="225px" height="" class="logo" style="color: #000;">
							<p class="receiptShopContact" style="color: #000;">
							<p>PLUMBING . HYDRONICS . HVAC<br />
110 West Beaver Creek Rd. Unit 16<br />
Richmond Hill, ON L4B 1J9<br />
905.597.4597  -  https://www.mekcosupply.com/<br />
</p>
					</p>
	</div>

					<h1 class="receiptTypeTitle">
																		Sales Receipt														</h1>

					<p class="date" id="receiptDateTime">
					07/08/2024 7:39 am
			</p>

					<p id="receiptInfo" class="details">
							
					<span class="receiptTicketIdField">
				<span class="receiptTicketIdLabel">
					Ticket: </span>
				<span id="receiptTicketId">
											220000034071
									</span>
				<br />
			</span>
		
		
					<span class="receiptRegisterNameField"><span class="receiptRegisterNameLabel">Register: </span><span id="receiptRegisterName">Mekco Shop</span><br /></span>
		
					<span class="receiptEmployeeNameField"><span class="receiptEmployeeNameLabel">Employee: </span><span id="receiptEmployeeName">Morteza</span><br /></span>
		
									<span class="receiptCompanyNameField"><span class="receiptCompanyNameLabel">Company: </span><span id="receiptCompanyName">Top Choice Plumbing</span><br /></span>
			
							<span class="receiptCustomerNameField"><span class="receiptCustomerNameLabel">Customer: </span><span id="receiptCustomerName">Hamed Asadi</span><br /></span>
			
			
			
						</p>

												<table class="sale lines">
			<tr>
				<th class="description">Items</th>

				
				
				<th class="quantity">#</th>

									<th class="amount">Price</th>
							</tr>
			<tbody>
										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			5M - Brass Pex Adapter  1/2&quot; Pex x 1/2&quot; FPT (Pack of 25) - 5MBP-41212-PFP-25		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						2
			 x
									$34.20
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$68.40
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			5 M - (Bag of 25) Brass Pex Adapter  1/2&quot; Pex x 1/2&quot; MPT- 5MBP-41212-PMT-25		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						2
			 x
									$29.93
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$59.86
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			5M - Brass Ears Drop Elbow  1/2&quot; Pex  x 1/2&quot; FPT  (Pack of 25)  - 5MBP-41212-PFTE-25		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						1
			 x
									$66.15
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$66.15
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			5M-Brass Drop Ear TEE 1/2&quot; PEX x 1/2&quot; PEX x 1/2&quot; FPT - 5MBP-41212-PFET		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						20
			 x
									$3.73
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$74.60
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			Oatey - ( BOX of 100 ) - STUD GUARD 3 IN-33930		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						2
			 x
									$20.00
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$40.00
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			Oatey - ( BOX of 100 )  - STUD GUARD 6 IN. 18 GAUGE - 33919		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						1
			 x
									$35.64
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$35.64
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - Double Wye / Y (ALL HUB) 2&quot; x 2&quot; x 1 1/2&quot; x 1 1/2&quot; - 600569		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						1
			 x
									$5.84
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$5.84
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting -Flush Bushing (SPG X HUB) 2&quot; x 1 1/2&quot; - 601567		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						1
			 x
									$0.59
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$0.59
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - Wye / Y (HUB X HUB X HUB) 2&quot; - 600403		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						2
			 x
									$2.73
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$5.47
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - P-Trap (HUB X HUB) 2&quot; - 602334		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						2
			 x
									$5.66
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$11.32
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - Coupling (HUB X HUB) 2&quot; - 601138		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						10
			 x
									$0.72
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$7.25
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - 90 Elbow (HUB X HUB) 2&quot; - 600627		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						10
			 x
									$1.30
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$12.98
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - 90 Street Elbow (HUB X SPG) 2&quot; - 600742		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						5
			 x
									$2.17
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$10.84
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - 45 Elbow (HUB X HUB) 2&quot; - 600916		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						10
			 x
									$1.12
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$11.16
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			ABS Fitting - 45 Street Elbow (SPG X HUB) 2&quot; - 600999		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						5
			 x
									$1.33
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$6.67
					</td>
	</tr>

										<tr>
		<td data-automation="lineItemDescription" class="description">
						<div class='line_description'>
			Dahl-All-Round Strapping 1/2&quot; 22GA Steel 25 -9010		</div>
				
					</td>

				
		
		<td data-automation="lineItemQuantity" class="quantity">
						2
			 x
									$3.91
									</td>

		<td data-automation="lineItemPrice" class="amount">
											$7.82
					</td>
	</tr>

							</tbody>
		</table>

					<table class="saletotals totals">
				<tbody id="receiptSaleTotals">
					<tr>
						<td width="100%">
															Subtotal
													</td>
						<td id="receiptSaleTotalsSubtotal" class="amount">
															$451.96
													</td>
					</tr>
											<tr><td>Discounts</td><td id="receiptSaleTotalsDiscounts" class="amount">-$27.37</td></tr>
																							<tr><td data-automation="receiptSaleTotalsTaxName" width="100%">HST ($424.59 @ 13%)</td><td data-automation="receiptSaleTotalsTaxValue" class="amount">$55.20</td></tr>
																						<tr><td width="100%">Total Tax</td><td id="receiptSaleTotalsTax" class="amount">$55.20</td></tr>
					<tr class="total"><td>Total</td><td id="receiptSaleTotalsTotal" class="amount">$479.79</td></tr>
									</tbody>
			</table>
			
						<h2 class="paymentTitle">Payments</h2>
			<table id="receiptPayments" class="payments">
				<tbody>
																		<!-- NOT Cash Payment -->
															<!-- Customer Account -->
								<tr>
																			<td class="label">Account Charge</td>
										<td id="receiptPaymentsCreditAccountChargeValue" class="amount">$479.79</td>
																	</tr>
																							<tr><td colspan="2"></td></tr>
												
				</tbody>
			</table>
		
										
											
											
					
									<h2 class="footerSectionTitle">Store Account</h2>
				<table class="totals">
											<tr>
							<td width="100%">Balance Owed: </td>
							<td class="amount">$18253.07</td>
						</tr>
									</table>
																											
	
				
								
				
				<p id="receiptNote" class="note" style="color: #000;">*  8%  Re-stocking fee will be applicable.<br />
* Mekco Supply Invoice must be presented at the time.<br />
<br />
This Sales Order is subject to Mekco Supply Inc's Terms and Conditions of Sale (Mekco terms), available at https://www.mekcosupply.com/terms-and-conditions-of-sale/ (&quot;Site&quot;).<br />
H.S.T. No: 749963286RT001</p>
					

																																																																																												
					<p id="receiptThankYouNote" class="thankyou">
													Thank You Hamed Asadi!
											</p>
				
									<p class="barcodeContainer">
						<!--<img id="barcodeImage" height="50" width="250" class="barcode" src="/barcode.php?type=receipt&number=220000034071&hide_text=">-->
						<img src="img/barcode.jpg">
					</p>
				
															
							</div>

			<!-- replace.email_custom_footer_msg -->
						<script src="https://d2o5po5b88zacb.cloudfront.net/dist/assets/lshash-90b03ce/js/runtime-cb61ef2490370fce6d71.js.gz" crossorigin="anonymous"></script><script src="https://d2o5po5b88zacb.cloudfront.net/dist/assets/lshash-90b03ce/js/vendors-App~Login~Oauth~Api~Branding~printTemplates-dc2405b256441bc5cad3.js.gz" crossorigin="anonymous"></script><script src="https://d2o5po5b88zacb.cloudfront.net/dist/assets/lshash-90b03ce/js/printTemplates-dfcec73536100848dfb6.js.gz" crossorigin="anonymous"></script>									<script type="text/javascript">
											var printer_name = "receipt";
					
					try {
						window.focus();
						// Auto print function disabled
                        // window.merchantos.print.print(printer_name);
					} catch (e) {
						// do nothing
					}
				</script>
						</body>
</html>