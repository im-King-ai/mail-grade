用于及时知道自己的成绩，因为广财教务系统出了成绩也不通知
# -在py文件中填入邮箱和邮箱授权码
SENDER_EMAIL = ''   此处填发送邮箱的邮箱账号<br>
SENDER_PASSWORD = ''   此处填发送邮箱的授权码<br>
RECEIVER_EMAIL = ''    此处填接受邮箱的邮箱账号<br>

# -在py文件中填入教务系统的账号和密码
user = User（账号，密码）<br>
每小时查询一次成绩，如果有新的成绩出了的话，就会发送邮件到邮箱，会显示出成绩的科目和成绩。
