#coding=utf-8
from string import Template
import  os , string   , logging ,re
import  setting ,interface
from utls.pattern import end_keeper


# from interface import
from rg_io import *
# from error import *
# from lang.patterns import *

# class rg_shell:
#     @staticmethod
#     def rg(cmd):
#         rgcmd  = "/home/q/tools/rigger/rigger %s" %cmd
#         return rgcmd
#     def pylon(cmd) :
#         rgcmd  = "/home/q/tools/rigger/rigger/pylon %s" %cmd
#         return rgcmd


class shexec:
    DO        = True
    SUDO      = False

    have_cond = False
    cond_fun  = None
    exec_fun  = None
    @staticmethod
    def cond_exec(cond_fun,exec_fun):
        shexec.have_cond = True
        shexec.cond_fun = cond_fun
        shexec.exec_fun = exec_fun
        pass

    @staticmethod
    def clear_cond_exec():
        shexec.have_cond = False
        shexec.cond_fun  = None
        shexec.exec_fun  = None
        pass
    @staticmethod
    def debug():
        shexec.DO= False

    @staticmethod
    def out2txt(cmd,txt):
        with open(txt,"w") as f :
            f.write("export PATH=/usr/local/bin:/usr/local/sbin:/usr/bin/:/usr/sbin/:/bin:/sbin\n")
            f.write(cmd)

    @staticmethod
    def sudo_enable():
        shexec.SUDO= True

    @staticmethod
    def sudo_disable():
        shexec.SUDO= False


    @staticmethod
    def execmd(cmd,check=True, okcode= [0] ,tag = None ):
        if shexec.have_cond :
            if shexec.cond_fun and shexec.cond_fun(cmd,tag):
                return shexec.exec_fun(cmd,check,okcode)
        return shexec.execmd_impl(cmd,check,okcode)

    @staticmethod
    def execmd_impl(cmd,check=True, okcode= [0] ):
        # cmd_txt =  setting.tmp_file("sh")
        cmd_txt  = "/tmp/rigger-ng.cmd"
        cmd     =  re.sub(r'/bin/php ' ,'/bin/php  -d error_reporting="E_ALL&~E_NOTICE" ',cmd)
        if setting.debug :
            rgio.simple_out(cmd)

        if shexec.DO  :
            shexec.out2txt(cmd,cmd_txt)
            with end_keeper(lambda : os.system( " rm %s " %cmd_txt ) )   as keeper :
                os.system("chmod +x " +  cmd_txt)
                if shexec.SUDO  :
                    sudo_cmd    = "sudo " + cmd_txt
                    rcode       = os.system(sudo_cmd)
                    if setting.debug  :
                        rgio.simple_out("sudo system code: %s" % rcode )
                    if check and rcode not in  okcode :
                        raise interface.rigger_exception("shell execute have error! code: %d  cmd:\n%s " %(rcode ,cmd))
                    return 0
                else:
                    rcode = os.system( cmd_txt)
                    if setting.debug  :
                        rgio.simple_out("system code: %s" % rcode )
                    if check and rcode not in  okcode :
                        raise interface.rigger_exception("shell execute have error! code: %d  cmd:\n%s" %(rcode,cmd) )
                    return  0
        else :
            return 0
        return 1

class scope_sudo:
    def __init__(self,need):
        self.need = need
    def __enter__(self):
        if self.need:
            shexec.sudo_enable()
    def __exit__(self,exc_type,exc_value,traceback):
        if self.need:
            shexec.sudo_disable()
