/**
 * 活动参加申请交互逻辑，主要是表单验证
 * 金额计算，动态生成服务项。。。
 *
 * by lwz7512@2016/05/20
 */
$(function(){

  var defaultMemberCount = 1;
  var activityID = $('#data-actID').html();
  var actdetails;//活动详情，其中的金额计算要用到
  var insurancecfg;//取到的保险配置
  var customerProfile;//取到的个人信息(积分)选项
  var total_fees = 0;//订单总金额，实时计算而来



  // 获取活动详情，主要是获取附加服务
  $.getJSON('/customer/activity/details?id='+activityID, function(result){
    actdetails = result;//保存下来后面计算金额时用到
    // console.log(result);
    createServiceItems(result['ext_fee_template']);
    // 第一次默认计算订单金额
    caculateTotalFees();
  });

  // 获取个人(代金券)选项
  $.getJSON('/customer/ajax/vouchers/mine', function(result){
    voucherscfg = result;//保存下来后边计算时需要
    createVouchersItems(result);
    caculateTotalFees();//重新算一次
  });

  // 获取保险选项
  $.getJSON('/customer/insurancecfg', function(result){
    insurancecfg = result;//保存下来后边计算时需要
    createInsuranceItems(result);
    caculateTotalFees();//重新算一次
  });

  // 获取个人信息(积分)选项
  $.getJSON('/customer/ajax/profile/mine', function(result){
    customerProfile = result;//保存下来后边计算时需要
    createBonusItems(result);
    caculateTotalFees();//重新算一次
  });

  // 生成代金券选项
  function createVouchersItems(items){
    var innerHTML = '';
    for(var i in items){
      innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
      innerHTML += '  <label class="ui-checkbox" >';
      innerHTML += '    <input type="checkbox" name="vouchers" value="'+items[i]['_id']+'"';
      innerHTML += '      data-fee="'+items[i]['amount']+'">';
      innerHTML += '  </label>';
      innerHTML += '  <p class="near-full-width">';
      innerHTML += '    <a>可用代金券抵</a>';
      innerHTML += '    <span id="vouchers_label" class="flt-right">-'+items[i]['amount']+'元</span>';
      innerHTML += '  </p>';
      innerHTML += '</div>';
    }
    $('.voucherscfg').html(innerHTML);
  }

  // 生成积分选项
  function createBonusItems(item){
    var innerHTML = '';
      innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
      innerHTML += '  <label class="ui-checkbox" >';
      innerHTML += '    <input type="checkbox" name="bonus" value="'+item['bonus']+'"';
      innerHTML += '      data-fee="'+item['bonus']+'">';
      innerHTML += '  </label>';
      innerHTML += '  <p class="near-full-width">';
      innerHTML += '    <a>可用积分抵</a>';
      innerHTML += '    <span id="bonus_label" class="flt-right">-'+item['bonus']+'元</span>';
      innerHTML += '  </p>';
      innerHTML += '</div>';
    $('.bonuscfg').html(innerHTML);
  }

  // 生成保险选项
  function createInsuranceItems(items){
    var innerHTML = '';
    for(var i in items){
      innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
      innerHTML += '  <label class="ui-checkbox" >';
      innerHTML += '    <input type="checkbox" name="insurance" value="'+items[i]['_id']+'"';
      innerHTML += '      data-fee="'+items[i]['amount']+'" checked>';
      innerHTML += '  </label>';
      innerHTML += '  <p class="near-full-width">';
      innerHTML += '    <a>'+items[i]['title']+'</a>';
      innerHTML += '    <span class="flt-right">'+items[i]['amount']+'元</span>';
      innerHTML += '  </p>';
      innerHTML += '</div>';
    }
    $('.insurancecfg').html(innerHTML);
  }

  // 生成附加服务选项
  function createServiceItems(items){
    $('.ui-loading-wrap').addClass('hidden');//隐藏进度条
    // console.log(items);
    var innerHTML = '';
    for(var i in items){
      innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
      innerHTML += '  <label class="ui-checkbox" >';
      innerHTML += '    <input type="checkbox" name="misc-service" value="'+items[i]['_id']+'"';
      innerHTML += '      data-fee="'+items[i]['fee']+'" checked>';
      innerHTML += '  </label>';
      innerHTML += '  <p class="near-full-width">';
      innerHTML += '    <a>'+items[i]['name']+'</a>';
      innerHTML += '    <span class="flt-right">'+items[i]['fee']+'元</span>';
      innerHTML += '  </p>';
      innerHTML += '</div>';
    }
    $('.appendixsvs').html(innerHTML);
  }

  // 计算订单金额
  function caculateTotalFees(){
    // 默认先以活动费用我基数
    // 使用已经保存的活动详情数据
    total_fees = parseInt( Number(actdetails.amount)*100 * defaultMemberCount);

    // 累加附加费用
    $('.appendixsvs input[type="checkbox"]:checked').each(function(){
      var fee = Number( $(this).data('fee') );
      total_fees += parseInt( fee * 100 * defaultMemberCount);
    });
    // 累加保险费用
    $('.insurancecfg input[type="checkbox"]:checked').each(function(){
      var fee = Number( $(this).data('fee') );
      total_fees += parseInt( fee * 100 * defaultMemberCount);
    });

    // 减去代金券
    $('.voucherscfg input[type="checkbox"]:checked').each(function(){
      var fee = Number( $(this).data('fee') );
      total_fees -= parseInt( fee * 100);
      if (total_fees < 0) {
        total_fees = 0;
      }
    });

    var bonus_checked = false;
    // 计算是否使用积分
    $('.bonuscfg input[type="checkbox"]:checked').each(function(){
      var fee = Number( $(this).data('fee') );
      bonus_checked = true;
    });

    // 当前积分
    var bonus = parseInt( customerProfile['bonus'] * 100 );
    if (bonus_checked) {
      if (total_fees < bonus) {
        var use_bonus = total_fees / 100;
        total_fees = 0;

        var innerHTML = '';
        innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
        innerHTML += '  <label class="ui-checkbox" >';
        innerHTML += '    <input type="checkbox" name="bonus" value="' + use_bonus + '"';
        innerHTML += '      data-fee="' + use_bonus + '" checked>';
        innerHTML += '  </label>';
        innerHTML += '  <p class="near-full-width">';
        innerHTML += '    <a>可用积分抵</a>';
        innerHTML += '    <span class="flt-right">-' + use_bonus + '元</span>';
        innerHTML += '  </p>';
        innerHTML += '</div>';
        $('.bonuscfg').html(innerHTML);
      } else {
        total_fees = total_fees - bonus;
        var use_bonus = bonus / 100;

        var innerHTML = '';
        innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
        innerHTML += '  <label class="ui-checkbox" >';
        innerHTML += '    <input type="checkbox" name="bonus" value="' + use_bonus + '"';
        innerHTML += '      data-fee="' + use_bonus + '" checked>';
        innerHTML += '  </label>';
        innerHTML += '  <p class="near-full-width">';
        innerHTML += '    <a>可用积分抵</a>';
        innerHTML += '    <span class="flt-right">-' + use_bonus + '元</span>';
        innerHTML += '  </p>';
        innerHTML += '</div>';
        $('.bonuscfg').html(innerHTML);
      }
    } else {
      var use_bonus = bonus / 100;

      var innerHTML = '';
       innerHTML += '<div class="ui-form-item ui-form-item-checkbox ui-border-b">';
       innerHTML += '  <label class="ui-checkbox" >';
       innerHTML += '    <input type="checkbox" name="bonus" value="' + use_bonus + '"';
       innerHTML += '      data-fee="' + use_bonus + '">';
       innerHTML += '  </label>';
       innerHTML += '  <p class="near-full-width">';
       innerHTML += '    <a>可用积分抵</a>';
       innerHTML += '    <span class="flt-right">-' + use_bonus + '元</span>';
       innerHTML += '  </p>';
       innerHTML += '</div>';
       $('.bonuscfg').html(innerHTML);
    }

    total_fees = total_fees / 100;
    $('.total_fees').html(total_fees);
  }

  // ------ 微信支付提交 -------
  // 要动态添加字段
  $('#wexin-pay-btn').click(function(){
    // 成员数
    var members = $("<input>").attr("type", "hidden").attr("name", "applicant_num").val(defaultMemberCount);
    $('#apply-form').append(members);

    // 服务项
    var ext_feeIDs = [];
    $('.appendixsvs input[type="checkbox"]:checked').each(function() {
       ext_feeIDs.push($(this).val());
     });
    // 提交一个数组
    var ext_fees = $("<input>").attr("type", "hidden").attr("name", "ext_fees").val(JSON.stringify(ext_feeIDs));
    $('#apply-form').append(ext_fees);

    // 保险选项
    var insuranceIDs = [];
    $('.insurancecfg input[type="checkbox"]:checked').each(function(){
      insuranceIDs.push($(this).val());
    });
    // 保险选项也是id数组
    var insurances = $("<input>").attr("type", "hidden").attr("name", "insurances").val(JSON.stringify(insuranceIDs));
    $('#apply-form').append(insurances);

    // 代金券选项
    var vouchersArray = [];
    $('.voucherscfg input[type="checkbox"]:checked').each(function(){
      vouchersArray.push($(this).val());
    });
    // 代金券选项对应的是数值数组
    var vouchers = $("<input>").attr("type", "hidden").attr("name", "vouchers").val(JSON.stringify(vouchersArray));
    $('#apply-form').append(vouchers);

    // 积分选项
    var bonusArray = [];
    $('.bonuscfg input[type="checkbox"]:checked').each(function(){
      bonusArray.push($(this).val());
    });
    // 积分选项对应的是数值数组
    var bonus = $("<input>").attr("type", "hidden").attr("name", "bonus").val(JSON.stringify(bonusArray));
    $('#apply-form').append(bonus);

    // 总金额
    var total_amount = $("<input>").attr("type", "hidden").attr("name", "total_amount").val(total_fees);
    $('#apply-form').append(total_amount);

    // 校验是否选择了免责协议
    // @2016/06/01
    var agreementChecked = $('input[name="exceptions"]:checked').length;
    if(!agreementChecked){
      // 弹出提示窗口
      $(".ui-dialog").dialog("show");
      return;
    }

    // 现在可以提交了
    $('#apply-form').submit();

    return false;//防止自动提交
  });

  $('.member-mns-btn').click(function(){
    if(defaultMemberCount==1) return;

    defaultMemberCount --;
    $('.member-count').html(defaultMemberCount);
    // 重新计算
    caculateTotalFees();
  });

  $('.member-add-btn').click(function(){
    defaultMemberCount ++;
    $('.member-count').html(defaultMemberCount);
    // 重新计算
    caculateTotalFees();
  });

  // 点选项重新计算
  $('.appendixsvs').click(function(){
    caculateTotalFees();
  });

  // 点选项重新计算
  $('.insurancecfg').click(function(){
    caculateTotalFees();
  });

  // 点选项重新计算
  $('.voucherscfg').click(function(){
    caculateTotalFees();
  });

  // 点选项重新计算
  $('.bonuscfg').click(function(){
    caculateTotalFees();
  });

// -------- 模拟的按钮交互效果 -------
// 必须使用触摸事件，不然没有反馈
// @2016/05/30
  $('.mock-green-btn').on('touchstart', function(){
    $(this).addClass('deep');
  });
  $('.mock-green-btn').on('touchend', function(){
    $(this).removeClass('deep');
  });
// -------- end of mockbtn --------





});
