/**
 * 添加活动成员模块
 * @2016/05/30
 */
$(function(){

  // 添加成员的页面所属元素
  var orderID = $('#data-ordID').html();
  //从隐藏域中获取
  var accountID = $('input[name="account_id"]').val();
  // 保存从后台取到的历史联系人，选择一个后添加到自己的表单中
  var contacts = {};

  // 根据订单申请人数来创建表单
  $.getJSON('/customer/order/details?id='+orderID, function(result){
    // console.log(result);
    createApplicantFormBy(Number(result.applicant_num));
    $('.ui-loading-wrap').addClass('hidden');//隐藏进度条
  });

  // TODO:
  // 获取当前用户曾经填过的申请人
  // 延时添加到表单中
  // @2016/06/14
  $.getJSON('/customer/contacts?id='+accountID, function(result){
    // console.log(result);
    // 数组转字典
    for(var i in result){
      var contactID = result[i]['_id'];
      contacts[contactID] = result[i];
    }
    // 延时添加，为了等待订单详情到达后...
    setTimeout(function(){
      var select = createApplicatnSelect(result);
      // 添加联系人选项
      $('.applicant').each(function(){
        $(this).prepend(select);//显示
      });
      // 添加切换动作
      $('select[name="contact"]').change(function(){
        var contactID = $(this).val();
        var contact = contacts[contactID];
        // 回填表单
        var applicantForm = $(this).parents('.applicant');
        applicantForm.find('input[name="name"]').val(contact.name);
        applicantForm.find('input[name="id_code"]').val(contact.id_code);
        applicantForm.find('input[name="height"]').val(contact.height);
        applicantForm.find('input[name="phone"]').val(contact.phone);
        applicantForm.find('select[name="gender"]').val(contact.gender);
      });

    }, 500);
  });

  /**
   * 生成历史参加人员选项
   * @2016/06/14
   */
  function createApplicatnSelect(applycants){
    var select =  '';
    select += '<div class="ui-form-item ui-border-b">';
    select += '  <label>历史记录</label>';
    select += '  <div class="ui-select">';
    select += '    <select name="contact">';
    select += '      <option value="0">选择参加人员</option>';
    for(var i in applycants){
      var app = applycants[i];
      select += '    <option value="'+app['_id']+'">'+app['name']+'</option>';
    }
    select += '    </select>';
    select += '  </div>';
    select += '</div>';
    return select;
  }


  /**
   * 创建参加人员表单 @2016/05/31
   */
  var applicantForm = '';
  function createApplicantFormBy(num){
    for(var i=0; i<num; i++){
      // 新增人员标题
      applicantForm += '<div class="ui-whitespace maring-top-10">';
      applicantForm += '  <p class="ui-txt-info font-normal ">';
      applicantForm += '    新增参加人员';
      applicantForm += '  </p>';
      applicantForm += '</div>';
      // 外围加容器、加人员序号以区分
      applicantForm += '<div class="ui-whitespace ui-border-t applicant" data-id="'+(i+1)+'">';
      // 从历史记录选择
      // 动态创建...
      // 表单项开始
      applicantForm += '  <div class="ui-form-item ui-border-b">';
      applicantForm += '    <label>真实姓名</label>';
      applicantForm += '    <input type="text" name="name" placeholder="与身份证上姓名相符">';
      applicantForm += '  </div>';
      // 性别
      applicantForm += '  <div class="ui-form-item ui-border-b">';
      applicantForm += '    <label>性别</label>';
      applicantForm += '    <div class="ui-select">';
      applicantForm += '      <select name="gender">';
      applicantForm += '        <option value="male">男</option>';
      applicantForm += '        <option value="female">女</option>';
      applicantForm += '      </select>';
      applicantForm += '    </div>';
      applicantForm += '  </div>';
      // 身份证号码
      applicantForm += '  <div class="ui-form-item ui-border-b">';
      applicantForm += '    <label class="ui-border-r">';
      applicantForm += '      身份证号码';
      applicantForm += '    </label>';
      applicantForm += '    <input type="text" name="id_code" placeholder="18位身份证号码">';
      applicantForm += '  </div>';
      // 出生年月
      // applicantForm += '  <div class="ui-form-item ui-border-b">';
      // applicantForm += '    <label class="ui-border-r">';
      // applicantForm += '      出生年月';
      // applicantForm += '    </label>';
      // applicantForm += '    <input type="text" name="birth_day" placeholder="格式：YYYY-MM-DD">';
      // applicantForm += '  </div>';
      // 身高
      applicantForm += '  <div class="ui-form-item ui-border-b">';
      applicantForm += '    <label class="ui-border-r">';
      applicantForm += '      身高(cm)';
      applicantForm += '    </label>';
      applicantForm += '    <input type="number" name="height" placeholder="厘米">';
      applicantForm += '  </div>';

      // 手机号码
      applicantForm += '  <div class="ui-form-item ui-border-b">';
      applicantForm += '    <label class="ui-border-r">';
      applicantForm += '      手机号码';
      applicantForm += '    </label>';
      applicantForm += '    <input type="number" name="phone" placeholder="11位">';
      applicantForm += '  </div>';

      // 备注说明
      applicantForm += '  <div class="ui-form-item ui-form-item-textarea ui-border-b">';
      applicantForm += '    <label class="ui-border-r">';
      applicantForm += '      备注说明';
      applicantForm += '    </label>';
      applicantForm += '    <textarea name="note" placeholder="特殊情况说明，可不填" maxlength="50"></textarea>';
      applicantForm += '  </div>';

      // 一组结束
      applicantForm += '</div>';
    }

    $('#applicants-form').append(applicantForm);
  }

  // 保存新增人员到历史记录
  $('#addmbr-btn').click(function(){
    var members = [];
    $('.applicant').each(function(){
      var member = {};
      member.name = $(this).find('input[name="name"]').val();
      member.birth_day = $(this).find('input[name="birth_day"]').val();
      member.height = $(this).find('input[name="height"]').val();
      member.id_code = $(this).find('input[name="id_code"]').val();
      member.phone = $(this).find('input[name="phone"]').val();
      member.gender = $(this).find('select[name="gender"]').val();
      member.note = $(this).find('textarea[name="note"]').val();//备注@2016/06/15
      members.push(member);
    })
    // console.log(members);

    var mbrs_input = $("<input>").attr("type", "hidden").attr("name", "applicants").val(JSON.stringify(members));
    $('#applicants-form').append(mbrs_input);

    // TODO: 做表单空值验证
    var checkresult = true;
    $('input').each(function(){
      if(!$(this).val()) checkresult = false;
    });
    if(!checkresult){
      createDialog('注意', '输入项不能为空！');
      return;
    }
    // TODO: 身份证验证
    checkresult = true;
    $('input[name="id_code"]').each(function(){
      var id_code = $(this).val();
      // 引用一个全局的函数
      var info = getIdCardInfo(id_code);
      if(!info || !info.isTrue) checkresult = false;
    });
    if(!checkresult){
      createDialog('注意', '身份证格式不正确，请重新填写');
      return;
    }
    // TODO: 手机号码验证
    checkresult = true;
    $('input[name="phone"]').each(function(){
      var phone = $(this).val();
      var info = checkMobile(phone);
      if(!info) checkresult = false;
    });
    if(!checkresult){
      createDialog('注意', '手机号码格式不正确，请重新填写');
      return;
    }

    // 现在可以提交了
    $('#applicants-form').submit();

    return false;
  });

  /**
   * <div class="ui-dialog">
     <div class="ui-dialog-cnt">
       <header class="ui-dialog-hd ui-border-b">
         <h3>注意</h3>
       </header>
       <div class="ui-dialog-bd">
         <h4>输入项不能为空</h4>
       </div>
       <div class="ui-dialog-ft">
         <button type="button" data-role="button">好 的</button>
       </div>
     </div>
   </div>
   */
  function createDialog(title, content){
    var dialog = '<div class="ui-dialog">';
        dialog +=' <div class="ui-dialog-cnt">';
        dialog +='  <header class="ui-dialog-hd ui-border-b">';
        dialog +='    <h3>';
        dialog +=     title;
        dialog +='    </h3>';
        dialog +='  </header>';
        dialog +='  <div class="ui-dialog-bd">';
        dialog +='    <h4>';
        dialog +=     content;
        dialog +='    </h4>';
        dialog +='  </div>';
        dialog +='  <div class="ui-dialog-ft">';
        dialog +='    <button type="button" data-role="button">好 的</button>';
        dialog +='  </div>';
        dialog +=' </div>';
        dialog +='</div>';

    $('body').append(dialog);

    var dia = $('.ui-dialog').dialog("show");

    dia.on("dialog:action",function(e){
        console.log(e.index)
    });
    dia.on("dialog:hide",function(e){
      $('.ui-dialog').remove();
    });
  }




});
