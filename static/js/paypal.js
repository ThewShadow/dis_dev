paypal.Buttons({
    style: {
        layout: 'horizontal',   // horizontal | vertical
        size:   'responsive',   /* medium | large | responsive*/
        shape:  'pill',         /* pill | rect*/
        color:  'gold',         /* gold | blue | silver | black*/
        tagline: 'false'          /* true | false */
    },
    createOrder: function(data, actions) {
        return actions.order.create({
            purchase_units: [{
                env: "sandbox",
                client: {
                    sandbox:
                        "Aa8PaxYQyyYIvzISVFbZ6PJbZlc_DRFl0QtTH7IcwYpTJz9lggiHR9Co4n4qgi4secbvd8zeDpq30-Zd",
                   },
                custom_id: getCookie("sub_id"),
                amount: {
                    value: getCookie("offer_price"),
                }
            }]
        });
    },
    onApprove: function(data, actions) {

        return actions.order.capture().then(function(details) {
            console.log("details" + JSON.stringify(details));
            $.ajax({
                type: "POST",
                url: "/service/paypal/receiving_payment/",
                contentType: "application/json",
                data: JSON.stringify(details)

            }).done(function (resp) {
                    window.location.replace("/service/paypal_return/")
            }).fail(function (resp) {
                    window.location.replace("/paypal_error/")
            });
        });
    }
}).render('#paypal-button-container');
