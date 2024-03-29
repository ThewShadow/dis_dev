const loginPopUp = document.getElementById('popup_1');
const RegistrationPopUp =  document.getElementById("popup_2");
const VerifyPopUp =  document.getElementById("popup_3");
const VerifySuccessPopUp =  document.getElementById("popup_4");
const CreateSubsctiptionPopUp = document.getElementById('popup_8');
const PaymentPopUp = document.getElementById('popup_9');
const ResetPasswordEmailPopUp = document.getElementById('popup_5');
const ResetPasswordCodePopUp = document.getElementById('popup_6');
const NewPasswordPopUp = document.getElementById('popup_7');
const SubscriptionPaidPopUp = document.getElementById("popup_12")
const CryptoPaymentPopUp = document.getElementById('popup_11')
const LogoutPopUp = document.getElementById('popup_13')
const SupportEmailPopUp = document.getElementById('popup_14')


$('.login-link').click(function (event){
    event.preventDefault();
    popupClose(RegistrationPopUp);
    popupOpen(loginPopUp)
});

$('.logout-button').click(function (event) {
    event.preventDefault();
    popupOpen(LogoutPopUp);
});

$('.popup__logout-cancel').click(function (event) {
    event.preventDefault();
    popupClose(LogoutPopUp);
});

$('.register-link').click(function (event){
    event.preventDefault();
    popupClose(loginPopUp)
    popupOpen(RegistrationPopUp);
});

$('.login-button').click(function (event){
    event.preventDefault();
    login();
});

$('.register-button').click(function (event){
    event.preventDefault();
    register();
});

$('.register_success__button_ok').click((e)=>{
    popupClose(VerifySuccessPopUp)
})

$(".apply-button").click(function (event) {
     event.preventDefault()
     createSubscription()
});

$('.forgot-pass-link').click(function (event){
    event.preventDefault();
    popupClose(loginPopUp);
    popupOpen(ResetPasswordEmailPopUp)
});


$(".forget-pass-submit").click(function (event) {
     event.preventDefault();
     resetPasswordStart();
});

$(".forget-pass-confirm").click(function (event) {
     event.preventDefault();
     resetPasswordConfirm();
});


$(".forget-pass-complete").click(function (event) {
     event.preventDefault();
     resetPasswordComplete();
});


$("#paid-subscr-ok").click(function () {
    event.preventDefault();
    popupClose(SubscriptionPaidPopUp)
});


$("#crypto-pay-button").click(function () {
    event.preventDefault();
    generate_crypto_token()
});

$('.email_support').click((e) => {
    e.preventDefault();
    popupOpen(SupportEmailPopUp)
})

$('#create_task').click((e) => {
    e.preventDefault();
    createTask()
})

$(".get-started-button").click(function (event){
    event.preventDefault();
    var sub_id = this.id;
    $.post(document.location.origin+"/service/is_authenticated/")
    .done(function (resp) {
        document.cookie = "offer_id="+ sub_id +"; path=/";
        popupOpen(CreateSubsctiptionPopUp);
    })
    .fail(function (resp) {
       if (resp.status == 401) {
           popupOpen(loginPopUp)
        }
    });
});


$(".managment__filters").submit((event)=>{
    document.cookie = "q="+$('.managment__filters input[name=q]').val()+"; path=/";
    document.cookie = "show="+$('.managment__filters input[name=show]').val()+"; path=/";
    $(".managment__filters").submit()
})

function createTask() {
    var form_name = "create-task-form";
    $(`#${form_name} .email_errors`).empty();
    $(`#${form_name} .description_errors`).empty();
    var data =new FormData(document.getElementById('create-task-form'));
    $.ajax({
        type: "POST",
        url: document.location.origin+"/service/create_support_task/",
        data: data,
        processData: false,
        contentType: false,
        statusCode: {
            200: (resp) => {
                if (resp['success']) {
                    popupClose(SupportEmailPopUp);
                }
            },
            400: (resp) => {
                showMessages(resp, form_name);
            }
        }
    });
}

function generate_crypto_token() {
    var form_id = "crypto-payment-form";
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    json = getJson($('#csrf_ajax_token').serializeArray());
    json["type-payment"] = $('.select-currency option:selected'). text();
    json["type-blockchain"]= $('.select-blockchain option:selected'). text();
    $.post(document.location.origin+"/service/payments/crypto/create/", json)
    .done(function (resp) {
              if (resp['success']) {

                popupClose(PaymentPopUp)
                popupOpen(CryptoPaymentPopUp)

                $("#payment-link").html(resp["pycode"])
                $("#amount").html(resp["price"] +" "+ resp["currency"])
                $("#blockchain_name").html(resp["blockchain"])
              }
           })
     .fail(function (resp) {
            showMessages(resp, form_id);
        });
}


function login() {
    var form_id = "login-form";
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    $("#"+form_id+" .password_errors").empty();
    $("#"+form_id+" .email_errors").empty();
    $("#"+form_id+" .message").empty();
    $.post(document.location.origin+"/service/accounts/login/", json)
     .done(function (resp) {
         if (resp['success']) {
            popupClose(loginPopUp);
            window.location.reload();
        }
        }).fail(function (resp) {
            showMessages(resp, form_id);
      });
}

function register() {
    var form_id = "registration-form"
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    if ($('input[name=agreement]').is(':checked')) {
        json['agreement'] = true;
    } else {
        json['agreement'] = true;
    }

    $("#"+form_id+" .password_errors").empty();
    $("#"+form_id+" .email_errors").empty();
    $("#"+form_id+" .username_errors").empty();
    $("#"+form_id+" .message").empty();
    $('.agreement_error').empty();
    $.post(document.location.origin+"/service/accounts/register/", json)
     .done(function (resp) {
        if (resp['success']) {
            popupClose(RegistrationPopUp);
            popupOpen(VerifyPopUp);
        }
    }).fail(function (resp) {
        showMessages(resp, form_id);

        $('.agreement_error').append(resp["responseJSON"]["error_messages"]["agreement"][0])
    });
}


function verify() {
    var form_id = "verify-email-form"
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    $("#"+form_id+" .message").empty();
    $.post(document.location.origin+"/service/accounts/activation_email/", json)
     .done(function (resp) {
            if (resp['success']) {
                popupClose(VerifyPopUp);
                popupOpen(VerifySuccessPopUp);
            }
    }).fail(function (resp) {
            showMessages(resp, form_id)
    });
}


function resetPasswordStart() {
    var form_id = "forget-pass-email-form"
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    $("#"+form_id+" .message").empty();
    $("#"+form_id+" .email_errors").empty();
    $.post(document.location.origin+"/service/accounts/reset_password/start/", json)
     .done(function (resp) {
            if (resp['success']) {
                popupClose(ResetPasswordEmailPopUp);
                popupOpen(ResetPasswordCodePopUp);
            }
    }).fail(function (resp) {
            showMessages(resp, form_id)
    });
}

function resetPasswordConfirm() {
    var form_id = "forget-pass-code-form"
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    $("#"+form_id+" .message").empty();
    $("#"+form_id+" .verify_code_errors").empty();


    $.post(document.location.origin+"/service/accounts/reset_password/confirm/", json)
     .done(function (resp) {
            if (resp['success']) {
                popupClose(ResetPasswordCodePopUp);
                popupOpen(NewPasswordPopUp);
            }
    }).fail(function (resp) {
            showMessages(resp, form_id)
    });
}

function resetPasswordComplete() {
    var form_id = "new-password-form"
    var register_form = $("#"+form_id).serializeArray();
    var json = getJson(register_form);
    $("#"+form_id+" .message").empty();
    $("#"+form_id+" .password1_errors").empty();
    $("#"+form_id+" .password2_errors").empty();
    $.post(document.location.origin+"/service/accounts/reset_password/complete/", json)
     .done(function (resp) {
            if (resp['success']) {
                popupClose(NewPasswordPopUp);
                popupOpen(loginPopUp);
            }
    }).fail(function (resp) {
            showMessages(resp, form_id)
    });
}


function createSubscription() {
    var form_id = "subscription_app_form";
    var form = $('#subscription_app_form');
    var data_array = form.serializeArray();
    var json = getJson(data_array);
    var offer_id = getCookie('offer_id');
    json['offer_id'] = offer_id;
    $("#"+form_id+" .email_errors").empty();
    $("#"+form_id+" .user_name_errors").empty();
    $("#"+form_id+" .phone_number_errors").empty();
    $("#"+form_id+" .service_password_errors").empty();
    $("#"+form_id+" .message").empty();
    if (offer_id.length) {
        $.post(document.location.origin+"/service/subscriptions/create/", json
        ).done(function (resp) {

            document.cookie = "sub_id="+resp.sub_id+"; path=/"
            document.cookie = "offer_price="+resp.offer_price+"; path=/"
            popupClose(CreateSubsctiptionPopUp);
            popupOpen(PaymentPopUp);
        }).fail(function (resp) {

            showMessages(resp, form_id);
        });
    }
}

function showMessages(data, form_id) {
    var messages= undefined
    if (typeof data === "string") {
             messages = jQuery.parseJSON(data["responseJSON"]);
    } else if (typeof data === "object") {
             messages = data["responseJSON"];
    }

    if (messages === undefined) {
        return;
    }
    if (messages["error_messages"] != undefined) {
        showErrorMessages(messages["error_messages"], form_id);
    }

    if (messages["message"] != undefined) {
        $("#"+form_id+" .message").append(messages["message"]);
    }
}

function showErrorMessages(messages, form_id) {
    const keys = Object.keys(messages);
    for (let i = 0; i < keys.length; i++) {
        const key = keys[i];
        var message_array= messages[key];
        $("#"+form_id+" ."+key+"_errors").empty();
        for (let i=0; i < message_array.length; i++) {
            let text = message_array[i];
            $("#"+form_id+" ."+key+"_errors").append(text);
        }
    }
}


function getCookie(cookieName) {
    let cookie = {};
    document.cookie.split(';').forEach(function(el) {
        let [key,value] = el.split('=');
        cookie[key.trim()] = value;
    });
    return cookie[cookieName];
}


function getJson(data_array) {
    var post_data = {};

    for (let i=0; i < data_array.length; i++) {
        prop = data_array[i];
        post_data[prop["name"]] = prop["value"];
    }
    return post_data;
}

if (getCookie("paid_success") == "True") {
    document.cookie = "paid_success=null; path=/"
    popupOpen(SubscriptionPaidPopUp)
}

if (getCookie("show_login") == "True") {
    document.cookie = "show_login=null; path=/"
    popupOpen(loginPopUp)
}

var show = getCookie('show')
var q = getCookie('q')
if (show != undefined && show.length) {
    $('.managment__filters input[name=show]').val(show)
}
if (q != undefined && q.length) {
    $('.managment__filters input[name=q]').val(q)
}