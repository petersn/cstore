#! /usr/bin/python

link.put(":Echo program running.")
link.put("prompt:String to echo: ")
string = link.get()
link.put(":" + string)
link.put("done")

