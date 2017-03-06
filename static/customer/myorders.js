/**
 * 我的订单页交互 @2016/06/07
 */
$(function(){



  // -------- 模拟的按钮交互效果 -------
  // 必须使用触摸事件，不然没有反馈
  // @2016/06/7
    $('.orders li').on('touchstart', function(){
      $(this).addClass('active');
    });
    $('.orders li').on('touchend', function(){
      $(this).removeClass('active');
    });
  // -------- end of mockbtn --------



});
