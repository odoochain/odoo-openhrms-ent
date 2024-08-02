/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillStart, onMounted, useRef} = owl
export class DynamicDashboard extends Component {
    setup(){
        this.actionService = useService("action");
        this.rpc = useService("rpc");
        this.product_count_graph = useRef("product_count_graph");
        this.product_shipment_chart = useRef("product_shipment_chart");
        this.annual_sales_chart = useRef("annual_sales_chart");
        this.total_sales_chart = useRef("total_sales_chart");
        this.orm = useService("orm");
        this.myChart = null;
        this.state = useState({
            product_count : false,
            customer_count : false,
            credit_note_total : false,
            amount_due : false,
            my_store : false,
            my_shipments : false,
            total_invoiced : false,
            sale_amount : false
        });
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
        })
        onMounted(()=> this.renderChart())
    }
    //Onchange of the main dependent values in dashboard
    onChangeDependantValues(ev){
        ev.stopPropagation();
        ev.preventDefault();
        if (ev.target.value === "this_year"){
            this.thisYearRecord()
        }
        else if (ev.target.value === "this_quarter"){
            this.thisQuarterRecord()
        }
        else if (ev.target.value === "this_month"){
            this.thisMonthRecord()
        }
        else if (ev.target.value === "this_week"){
            this.thisWeekRecord()
        }
    }
    //To render this year records in tiles
    thisYearRecord() {
        var self = this;
        this.orm.call(
            "magento.dashboard",
            "this_year",
            [[]]
        ).then(function(result){
            self.tiles_data(self, result);
        });
    }
    //To render this quarter records in tiles
    thisQuarterRecord(){
        var self = this;
        this.orm.call(
            "magento.dashboard",
            "this_quarter",
            [[]]
        ).then(function(result){
            self.tiles_data(self, result);
        })
    }
    //To render this month records in tiles
    thisMonthRecord(){
        var self = this;
        this.orm.call(
            "magento.dashboard",
            "this_month",
            [[]]
        ).then(function(result){
            self.tiles_data(self, result);
            if (result[8]['customers']){
                self.state.customer_count = result[8]['customers']
            }
            else{
                self.state.customer_count = "No Customers"
            }
            if (result[9]['products']){
                self.state.product_count = result[9]['products']
            }
            else{
                self.state.product_count = "No Products"
            }
        })
    }
    //To render this week record in tiles
    thisWeekRecord(){
        var self = this;
        this.orm.call(
            "magento.dashboard",
            "this_week",
            [[]]
        ).then(function(result){
            self.tiles_data(self, result);
        })
    }
    //Data's and counts in the tiles
    tiles_data(self, result){
        if (result[0]['sum']){
            self.state.sale_amount = result[3]['symbol'] + ' ' + result[0]['sum']
        }
        else{
            self.state.sale_amount = "No Orders"
        }
        if (result[2]['due']){
            self.state.amount_due = result[3]['symbol'] + ' ' + result[2]['due']
        }
        else{
            self.state.amount_due = "No Due Amount"
        }
        if (result[4]['shipment']){
            self.state.my_shipments = result[4]['shipment']
        }
        else{
            self.state.my_shipments = "No Shipments"
        }
        if (result[5]['store']){
            self.state.my_store = result[5]['store']
        }
        else{
            self.state.my_store = "No Stores"
        }
        if (result[6]['invoiced']){
            self.state.total_invoiced = result[3]['symbol'] + ' ' + result[6]['invoiced']
        }
        else{
            self.state.total_invoiced = "No Invoice"
        }
        if (result[7]['credit_note']){
            self.state.credit_note_total = result[3]['symbol'] + ' ' + result[7]['credit_note']
        }
        else{
            self.state.credit_note_total = "No Credit Notes"
        }
    }
    //Rendering the chart at the first time with the initial values
    renderChart(){
        var self = this;
        // Rendering the chart of the product and its count
        this.orm.call(
            "magento.dashboard",
            "product_pi",
            [[]]
        ).then(function(result){
            var xValues = result['product_name'];
            var yValues = result['product_count'];
            var barColors = [
                        "#b91d47", "#00aba9", "#2b5797", "#e8c3b9",
                        "#F5F5DC", "#8A2BE2", "#1e7145", "#7FFF00",
                        "#DC143C", "#F0F8FF", "#8B008B", "#DAA520",
                        "#4B0082"];
            var pieChart = new Chart(self.product_count_graph.el, {
                type: 'doughnut',
                data: {
                        labels: xValues,//x axis
                        datasets: [{
                            label: 'Count', // Name the series
                            data: yValues, // Specify the data values array
                            backgroundColor: barColors,
                        }]
                    },
                    options: {
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        })
        // Renders the chart of the products shipped
        this.orm.call(
            "magento.dashboard",
            "product_ship",
            [[]]
        ).then(function(result){
            var xValues = result['product_name'];
            var yValues = result['product_count'];
            var barColors = ["#b91d47", "#00aba9", "#2b5797", "#e8c3b9",
                             "#F5F5DC", "#8A2BE2","#1e7145", "#7FFF00",
                             "#DC143C", "#F0F8FF", "#8B008B", "#DAA520",
                             "#4B0082"];
            var shipment_chart = new Chart(self.product_shipment_chart.el, {
                type: 'bar',
                data: {
                    labels: xValues,
                    datasets: [{
                        backgroundColor: barColors,
                        data: yValues,
                        label: 'Count', // Name the series
                        barPercentage: 1,
                        barThickness: 50, // Set the thickness to 20 pixels
                        maxBarThickness: 60, // Set the maximum thickness to 30 pixels
                        minBarLength: 0,
                        borderWidth: 1, // Specify bar border width
                        type: 'bar', // Set this data to a line chart
                        fill: false,
                        }]
                    },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            })
        });
        //Renders the annual growth chart
        this.orm.call(
            "magento.dashboard",
            "annual_growth",
            [[]]
        ).then(function(result){
            if(!result['total_year']){
                 $('#total_year').empty().append('No Orders');
            }
            else{
                $('#total_year').empty().append(result['currency'] + ' ' + result['total_year']);
            }
            var months = result['months'];
            var orders = result['orders'];
            var barColors = [
                    "#F5F5DC", "#8A2BE2", "#1e7145", "#7FFF00",
                    "#DC143C", "#F0F8FF", "#8B008B", "#DAA520",
                    "#b91d47", "#00aba9", "#2b5797", "#e8c3b9",
                    "#4B0082"];
            var annual_Chart = new Chart(self.annual_sales_chart.el, {
                type: 'line',
                data: {
                        labels: months,//x axis
                        datasets: [{
                            label: 'Count', // Name the series
                            data: orders, // Specify the data values array
                            backgroundColor: barColors,
                            lineTension: 0,
                            borderColor: '#424242',
                            borderWidth: 1, // Specify bar border width
                            type: 'line', // Set this data to a line chart
                            fill: false
                        }]
                    },
                    options: {
                    legend: {display: true},
                    scales: {
                        yAxes: [{
                        display: true,
                            ticks: {

                                beginAtZero: true,
                                steps: 1,
                                stepValue: 1,
                            }
                        }]
                    },
                    responsive: true, // Instruct chart js to respond nicely.
                    maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                }
            });
        })
        // Create a mock event object
        const mockEvent = {
            stopPropagation: () => {},
            preventDefault: () => {},
            target: { value: 'sales_today' }
        };
        // Call the TotalSale function with the mock event
        this.onChangeTotalSale(mockEvent);
        this.thisMonthRecord();
    }
    //Onchange on the total sale
    onChangeTotalSale(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var self = this;
        if (ev.target.value === 'sales_today'){
            this.orm.call(
            "magento.dashboard",
            "sales_today",
            [[]]
            ).then(function(result){
                $('#total_days_7').hide();
                $('#total_today').show();
                $('#total_today').empty().append(result['currency'] + ' ' + result['amt_today']);
                var date = ['Today'];
                var count = result['count_today'];
                var barColors = [
                        "#1e7145", "#7FFF00", "#DC143C", "#F0F8FF", "#8B008B", "#DAA520",
                        "#b91d47", "#00aba9", "#2b5797", "#e8c3b9", "#F5F5DC", "#8A2BE2",
                        "#4B0082"];
                if (self.myChart){
                    self.myChart.destroy();
                }
                self.myChart = new Chart(self.total_sales_chart.el, {
                    type: 'bar',
                    data: {
                            labels: date,//x axis
                            datasets: [{
                                label: 'Count', // Name the series
                                data: count, // Specify the data values array
                                backgroundColor: barColors,
                                barPercentage: 1,
                                barThickness: 50,
                                maxBarThickness: 60,
                                minBarLength: 0,
                                borderWidth: 1, // Specify bar border width
                                type: 'bar', // Set this data to a line chart
                                fill: false
                            }]
                        },
                    options: {
                        scales: {
                            yAxes: [{
                            display: true,
                                ticks: {

                                    beginAtZero: true,
                                    steps: 1,
                                    stepValue: 1,
                                }
                            }]
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                });
            });
        }
        else {
            //To render last seven days says details in chart
            this.orm.call(
            "magento.dashboard",
            "sales_7",
            [[]]
            ).then(function(result){
                $('#total_today').hide();
                $('#total_days_7').show();
                if(!result['amt_7']){
                    $('#total_days_7').empty().append('No Orders');
                }
                else{
                    $('#total_days_7').empty().append(result['currency'] + ' ' + result['amt_7']);
                }
                var date = result['days_name'];
                var count = result['count'];
                var barColors = [
                        "#DC143C", "#F0F8FF", "#8B008B", "#DAA520",
                        "#b91d47", "#00aba9", "#2b5797", "#e8c3b9",
                        "#F5F5DC", "#8A2BE2", "#1e7145", "#7FFF00",
                        "#4B0082"];
                if (self.myChart){
                    self.myChart.destroy();
                }
                self.myChart = new Chart(self.total_sales_chart.el, {
                    type: 'bar',
                    data: {
                            labels: date,//x axis
                            datasets: [{
                                label: 'Count', // Name the series
                                data: count, // Specify the data values array
                                backgroundColor: barColors,
                                barPercentage: 1,
                                barThickness: 40,
                                maxBarThickness: 50,
                                minBarLength: 0,
                                borderWidth: 1, // Specify bar border width
                                type: 'bar', // Set this data to a line chart
                                fill: false
                            }]
                        },
                        options: {
                        scales: {
                            yAxes: [{
                            display: true,
                                ticks: {

                                    beginAtZero: true,
                                    steps: 1,
                                    stepValue: 1,
                                }
                            }]
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                    }
                });
            });
        }
    }
    //Onclick total sale amount tile
    onClickSaleAmount(){
        this.actionService.doAction({
            name: _t("My Orders"),
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['magento', '=', true]],
            target: 'current',
        })
    }
    //Onclick total invoice amount tile
    onClickTotalInvoice(){
        this.actionService.doAction({
            name: _t("Invoice"),
            type: 'ir.actions.act_window',
            res_model: 'account.move',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
                domain: [['magento', '=', true], ['move_type', '!=', 'out_refund']],
            target: 'current',
        })
    }
    //Onclick total shipments tile
    onClickMyShipment(){
        this.actionService.doAction({
            name: _t("My Shipments"),
            type: 'ir.actions.act_window',
            res_model: 'shipment.shipment',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
        })
    }
    //Onclick My stores tile
    onClickMyStore(){
        this.actionService.doAction({
            name: _t("My Stores"),
            type: 'ir.actions.act_window',
            res_model: 'stores.magento',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
        })
    }
    //Onclick total due amount tile
    onClickAmountDue(){
        this.actionService.doAction({
            name: _t("Invoice"),
            type: 'ir.actions.act_window',
            res_model: 'account.move',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['magento', '=', true], ['move_type', '!=', 'out_refund']],
            target: 'current',
        })
    }
    //Onclick total credit note amount tile
    onClickTotalCreditNote(){
        this.actionService.doAction({
            name: _t("Credit Notes"),
            type: 'ir.actions.act_window',
            res_model: 'account.move',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['magento', '=', true], ['move_type', '=', 'out_refund']],
            target: 'current',
        })
    }
    //Onclick customers tile
    onClickCustomer(){
        this.actionService.doAction({
            name: _t("Customers"),
            type: 'ir.actions.act_window',
            res_model: 'res.partner',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['magento', '=', true]],
            target: 'current',
        })
    }
    //Onclick products tile
    onClickProduct(){
        this.actionService.doAction({
            name: _t("Products"),
            type: 'ir.actions.act_window',
            res_model: 'product.product',
            view_mode: 'tree,form,calendar',
            views: [[false, 'list'],[false, 'form']],
            domain: [['magento', '=', true]],
            target: 'current',
        })
    }
}
DynamicDashboard.template = "Magento_Dashboard"
registry.category("actions").add("magento_dashboard_tag", DynamicDashboard)
