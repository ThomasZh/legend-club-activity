/**
 * 移动端活动首页交互逻辑
 * by lwz7512@2016/05/18
 */
$(function(){

  // 获取分类
  $.getJSON('/customer/categories', function(result){
    // console.log(result);
    var items = '';
    for(var i in result){
      items += createCategoryItem(result[i]);
    }
    $('.mod-recommend ul').html(items);
  });

  // 先要获取热门活动
  $.getJSON('/customer/activity/popular', function(result){
    console.log(result);
    $('.ui-loading-wrap').addClass('hidden');
    $('.ui-slider').removeClass('hidden');

    var slides = '';
    for(var i in result){
      slides += createSlideBy(result[i]);
    }

    if(result.length>1){
      $('.ui-slider-content').html(slides);
    }else {
      $('.ui-slider-content').append(slides);
    }

    var slider = new fz.Scroll('.ui-slider', {
        role: 'slider',
        indicator: true,
        autoplay: true,
        interval: 3000
    });
  });

  /**
   * <li>
     <img src="/static/img/recommend1.png">
     <span class="recommend-info">沙漠</span>
   </li>
   */
  function createCategoryItem(item){
    var li = '<li data-id="'+item['_id']+'">';
        li +='  <img src="'+item['bk_img_url']+'">';
        li +='  <span class="recommend-info">'+item['title']+'</span>';
        li +='</li>';
    return li;
  }

  // 幻灯片格式：
  // <li>
  //  <span style="background-image:url(/static/img/tf1.jpg)"></span>
  //  <div class="slider-footer">
  //    第三张
  //  </div>
  // </li>
  // 详情地址：
  // /customer/activity/info?id=0a72b2801d9611e68aa86003089f4674

  // 生成幻灯片元素，包含可点击链接
  function createSlideBy(item){
    var li =  '<li><a href="/bike-forever/wechat/activity/info?id=' + item._id + '">';
        li += '<span style="background-image:url(';
        li +=   item.bk_img_url;
        li += ')"></span>'
        li += '<div class="slider-footer">';
        li +=   item.title;
        li += '</div>';
        li += '</a></li>';
    return li;
  }


});
