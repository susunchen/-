;

var option_set_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".wrap_option_set .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("正在处理!!请不要重复提交~~");
                return;
            }

            $(".wrap_option_set select[name=option_type]").select2({
            language: "zh-CN",
            width: '100%'
            });

            $(".wrap_option_set select[name=hall_id]").select2({
            language: "zh-CN",
            width: '100%'
            });

            var name_target = $(".wrap_option_set input[name=name]");
            var name = name_target.val();

            var option_type_target = $(".wrap_option_set select[name=option_type]");
            var option_type = option_type_target.val();

            var hall_id_target = $(".wrap_option_set select[name=hall_id]");
            var hall_id = hall_id_target.val();


            var option_id_target = $(".wrap_option_set input[name=option_id]");
            var option_id = option_id_target.val();

            var note_target = $(".wrap_option_set input[name=note]");
            var note = note_target.val();
            if( name.length < 1 ){
                common_ops.tip( "请输入符合规范的设备名称~~",name_target );
                return false;
            }
            if( option_id < 1 ){
                common_ops.tip( "请输入符合规范的设备编号~~",weighe_target );
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                name: name,
                option_type:option_type,
                hall_id: hall_id,
                option_id:option_id,
                note:note,

                id:$(".wrap_option_set input[name=id]").val()
            };

            $.ajax({
                url:common_ops.buildUrl( "/option/set" ),
                type:'POST',
                data:data,
                dataType:'json',
                success:function( res ){
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("/option/index");
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });


        });
    }
};

$(document).ready( function(){
    option_set_ops.init();
} );