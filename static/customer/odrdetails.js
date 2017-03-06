/**
 * 订单详情：
 * 查看订单内容、处理订单不同状态下的按钮指向地址
 * @2016/06/13
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


  // 根据订单详情，显示关键信息
  $.getJSON('/customer/order/details?id='+orderID, function(result){
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
       var inrHTML = '<p class="padding-left-10">'
        +ext_fees[i].name
        +'<span class="flt-right">'
        +ext_fees[i].fee
        +'元</span></p>';
      $('.extserv-items').append(inrHTML);
    }

    // 获取保险选项，并与订单中的配置比较显示
    var insurances = order['insurances'];
    for(var i in insurances){
      var inrHTML = '<p class="padding-left-10">'
        +insurances[i].name
        +'<span class="flt-right">'
        +insurances[i].fee
        +'元</span></p>';
      $('.insurance-items').append(inrHTML);
    }

    // 获取代金券选项，并与订单中的配置比较显示
    var vouchers = order['vouchers'];
    for(var i in vouchers){
      var inrHTML = '<p class="padding-left-10">'
        +'使用代金券抵'
        +'<span class="flt-right">-'
        +vouchers[i].fee
        +'元</span></p>';
      $('.vouchers-items').append(inrHTML);
    }

    // 获取积分选项，并与订单中的配置比较显示
    var bonus = order['bonus'];
    if (bonus < 0) {
      var inrHTML = '<p class="padding-left-10">'
        +'使用积分抵'
        +'<span class="flt-right">'
        +bonus
        +'元</span></p>';
      $('.bonus-items').append(inrHTML);
    }
  });

   // TODO: 如果有成员，是否要点击按钮查看成员呢？
  // 动态修改底部按钮地址和名称
  // 查询人员情况，来决定底部按钮显示文字和指向链接
  /*
  $.getJSON('/customer/order/applicants?id='+orderID, function(result){
    // 如果没有成员
    if(!result.length){
      $('#odr-status-btn').html('填写报名');
      var url = '/bike-forever/wechat/apply/action2?id='+actID+'&order_id='+orderID;
      // var url = '/customer/apply/action2?id='+actID+'&order_id='+orderID;
      $('#odr-status-btn').attr('href', url);
    }
  });
*/

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
