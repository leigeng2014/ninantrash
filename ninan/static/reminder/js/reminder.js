function pickme(){
    $('#id_previous_t').datetimepicker(
        {hourMin:6,hourMax:23,minDate:new Date(),dateFormat:'yy-mm-dd',
            timeFormat:'HH:mm:ss'}
    )
}

// 验证提醒方法提交时，各种数据是否为空
function validate_rmform(thisform)
{	
	with(thisform)
	{
		if (validate_required(ccp)==false)
		{
			alert('验证码不可为空');
			ccp.focus();
			return false;
		}
	}
}

// 获取验证码
function get_ccp()
{
    var vl_type=$('#id_name').val();
	var vl_value = $('#id_extra_info').val();
    var csrftoken=getCookie('csrftoken');
    var ajaxobj=new AJAXRequest();
    ajaxobj.url="/reminder/getccp/";
    ajaxobj.method="POST";
    ajaxobj.content="vl_type="+encodeURIComponent(vl_type);
	ajaxobj.content+="&vl_value="+encodeURIComponent(vl_value);
    ajaxobj.content+="&csrfmiddlewaretoken="+csrftoken;
    ajaxobj.callback=function(xmlObj){
        var jsondata=eval("("+xmlObj.responseText+")");
        if ( jsondata.rc == 200 )
        {
        	if (vl_type == "fetion")
        	{
        		alert("您的验证码已经发送至飞信"+vl_value);
        	}
        	else if (vl_type == "qqmail")
        	{
        		alert("您的验证码已发送至"+vl_value+"@qq.com,请查收");
        	}
        	$('#pop-ccp-success').popup(show);
        }
    }
    ajaxobj.send();
}
// validate_remindform
function validate_remindform(thisform){
	with(thisform)
		{
			// 检查输入的时间是否合法
			var selected_time = init_remind_time.value;
			if ( selected_time.indexOf(' ') == -1)
			{
				alert("初始时间字符串不是一个标准的时间串，请修改！");
				return false;
			}
			var selected_date = selected_time.replace(/-/g,'/');
			if ( (validateInputDate(selected_date))== false)
			{
				alert("请输入一个有效的时间格式。");
				return false;
			}// 时间检查结束

			// 检查类别选择是否正确
			var rd_type = remind_type.value;
			switch (rd_type)
			{
			case 'daily':
				break;
			case 'weekly':
				break;
			case 'workday':
				break;
			case 'once':
				break;
			case 'interval':
				if (isNaN(Number(cycle.value)))
				{
					alert('当选择每隔多少分时，间隔时间必须为数字！');
					return false;
				}
				else if  (Number(cycle.value)<=0)
				{
					alert('当选择每隔多少分时，间隔时间必须为正数！');
					return false;
				}
				else if (Number(cycle.value)<10)
				{
					alert('当选择每隔多少分时，间隔时间必须不小于10分钟！');
					return false;
				}
				else 
				{
					break;
				}
			case 'other':
				if (cycle.value.indexOf(',') != -1)
				{
					break;
				}
				else {
					alert('当选择自定义时，请用英文半角逗号分隔每周几。如，需要每周一三五提醒，则填入1,3,5');
					return false;
				}
			default :
				alert('提醒类别不合法!');
				return false;
			}// 类别检测结束

			// 检测是否包含空字段
			var strTitle = title.value;
			if (strTitle == ''||strTitle == null)
			{
				alert('标题不可为空！');
				return false;
			}
			var strContent = content.value;
			if (strContent == '' || strContent == null)
			{
				alert('内容不可为空！');
				return false;
			}// 空字段检测结束

			return true;
		}
}

function validateInputDate(inputDate){

	var strMaxDate = "9999-12-31";
	var strMinDate = "1989-04-11";
	var newDateValue = new Date(inputDate);
	if(isNaN(newDateValue))
	{
		alert('###'+inputDate);
		alert('初始时间不是一个时间格式!');
		return false;
	}
	var maxDate=new Date(fromymd2mdy(strMaxDate));
	if ((maxDate!=null)&&(newDateValue>maxDate))
	{
		alert('初始时间超过系统允许的最大时间');
		return false;
	}
	var minDate=new Date(fromymd2mdy(strMinDate));
	if ((minDate!=null)&&(newDateValue<minDate))
	{
		alert('初始时间小于系统允许的最小时间');
		return false;
	}
	return true;
}

function fromymd2mdy(val)
{
	if(!val) return;
	if(val.charAt(4) == '-')
	{
		var year = val.substr(0,4);
		var otherDate = val.substr(5);
		var blankIndex = otherDate.indexOf(" ");
		if(blankIndex > 0)
		{
			var monthday=otherDate.substring(0,blankIndex);
			val = monthday+"-"+year+otherDate.substr(blankIndex);
		}
		else
		{
			val = otherDate+"-"+year;
		}
	}
	return val;
}
