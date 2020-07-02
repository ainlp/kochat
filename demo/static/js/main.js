// variables
let userName = null;

// functions
function Message(arg) {
    this.text = arg.text;
    this.message_side = arg.message_side;

    this.draw = function (_this) {
        return function () {
            let $message;
            $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side).find('.text').html(_this.text);
            $('.messages').append($message);

            return setTimeout(function () {
                return $message.addClass('appeared');
            }, 0);
        };
    }(this);
    return this;
}

function getMessageText() {
    let $message_input;
    $message_input = $('.message_input');
    return $message_input.val();
}

function sendMessage(text, message_side) {
    let $messages, message;
    $('.message_input').val('');
    $messages = $('.messages');
    message = new Message({
        text: text,
        message_side: message_side
    });
    message.draw();
    $messages.animate({scrollTop: $messages.prop('scrollHeight')}, 300);
}

function greet() {
    setTimeout(function () {
        return sendMessage("Kochat 데모에 오신걸 환영합니다.", 'left');
    }, 1000);

    setTimeout(function () {
        return sendMessage("사용할 닉네임을 알려주세요.", 'left');
    }, 2000);
}

function onClickAsEnter(e) {
    if (e.keyCode === 13) {
        onSendButtonClicked()
    }
}

function setUserName() {
    let username = getMessageText();
    sendMessage(username, 'right');

    if (username != null && username.replace(" ", "" !== "")) {
        setTimeout(function () {
            return sendMessage("반갑습니다." + username + "님. 닉네임이 설정되었습니다.", 'left');
        }, 1000);
        setTimeout(function () {
            return sendMessage("저는 각종 여행 정보를 알려주는 여행봇입니다.", 'left');
        }, 2000);
        setTimeout(function () {
            return sendMessage("날씨, 미세먼지, 여행지, 맛집 정보에 대해 무엇이든 물어보세요!", 'left');
        }, 3000);

        return username;

    } else {
        setTimeout(function () {
            return sendMessage("올바른 닉네임을 이용해주세요.", 'left');
        }, 1000);

        return null;
    }
}

function requestAnswer(messageText) {
    $.ajax({
        url: "http://119.206.99.242:9999/request/" + userName + '/' + messageText,
        type: "GET",
        cache: false,
        dataType: "json",
        success: function (data) {
            console.log(data);
        },

        error: function (request, status, error) {
            let msg = "ERROR : " + request.status + "<br>";
            msg += +"내용 : " + request.responseText + "<br>" + error;
            console.log(msg);
        }
    });
}

function onSendButtonClicked() {
    if (userName == null) {
        userName = setUserName();
    } else {
        let messageText = getMessageText();
        requestAnswer(messageText);
    }
}