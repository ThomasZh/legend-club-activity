/**
 * 订单确认逻辑：本地开发测试用
 * 显示订单详情、提交微信支付
 * @2016/06/06
 */
$(function(){

  var order;//取到的订单详情
  var insurancecfg;//取到的保险配置

  // 活动编号
  var actID = $('#data-actID').html();
  // 添加成员的页面所属元素
  var orderID = $('#data-ordID').html();
  // 当前活动所定义的所有附加服务
  var services = $('#data-sevtmpl').html();
  var serviceMap = {};

  if(services) {
    services = JSON.parse(services);
    // console.log(services);
    for(var i in services){
      // services[i]['name'] + ' : ' + services[i]['fee'] + '元';
      serviceMap[services[i]['_id']] = {name: services[i]['name'], fee: services[i]['fee']};
    }
  }


  // 根据订单申请人数来创建表单
  $.getJSON('/customer/order/details?id='+orderID, function(result){
    // 保存订单到全局，后面用
    order = result;
    // console.log(result);

    $('.ui-loading-wrap').addClass('hidden');
    // 人数
    $('.applicant_num').html(order.applicant_num+'人');
    // 总金额
    $('.total_fees').html(order.total_amount);
    // 购买的附加服务
    var ext_fees = order['ext_fees'];
    for(var i in ext_fees){
      var item = serviceMap[ext_fees[i]];
      var inrHTML = '<p class="padding-left-10">'+item.name+'<span class="flt-right">'+item.fee+'元</span></p>';
      $('.extserv-items').append(inrHTML);
    }
  });

  // 获取保险选项
  $.getJSON('/system/insurancecfg', function(result){
    // console.log(result);
    var insuranceMap = {};
    for(var i in result){
      // result[i]['title'] + ' : ' + result[i]['amount'] + '元';
      insuranceMap[result[i]['_id']] = {name: result[i]['title'], fee: result[i]['amount']};
    }

    // FIXME, 延迟生成保险选项，可能订单信息没回来，等待下
    // @2016/06/14
    setTimeout(function(){
      var insurances = order['insurances'];
      if(!insurances) return;//空检查
      console.log('>>> create insurance item...');
      for(var i in insurances){
        var item = insuranceMap[insurances[i]];
        var inrHTML = '<p class="padding-left-10">'+item.name+'<span class="flt-right">'+item.fee+'元</span></p>';
        $('.insurance-items').append(inrHTML);
      }
    }, 500);
  });

  // TODO: 添加微信支付按钮点击交互动作
  $('#wexin-pay-btn').click(function(){
    location.href = '/customer/apply/action2?id='+actID+'&order_id='+orderID;
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
