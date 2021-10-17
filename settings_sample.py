# coding: UTF-8

button_setting = [
    {
        'name':'BUTTON1',   
        'mac':'FF:FF:FF:FF:FF:FF',
        'long_pushed_time':0.5,
        'command':{
            'connected':'echo "`date` connected" >>/tmp/test.txt',
            'ios_button':'echo "`date` ios_button_pushed" >>/tmp/test.txt',
            'ios_button_long':'echo "`date` ios_button_long_pushed" >>/tmp/test.txt',
            'android_button':'echo "`date` android_button_pushed" >>/tmp/test.txt',
            'android_button_long':'echo "`date` android_button_long_pushed" >>/tmp/test.txt'
        }
    },
    {
        'name':'BUTTON2',   
        'mac':'00:00:00:00:00:00',
        'long_pushed_time':0.5,
        'command':{
            'connected':'python3 sample1.py',
            'ios_button':'python3 sample2.py',
            'ios_button_long':'python3 sample3.py',
            'android_button':'python3 sample4.py',
            'android_button_long':'python3 sample5.py'
        }
    }
]

log = {
    'log_file_output':True,
    'log_level' : {
        'stdout':'DEBUG',
        'file':'INFO'
    }
}
