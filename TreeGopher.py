import queue
import threading
import protocols.gopher as gopher
import PySimpleGUI as sg
import pyperclip
import os
import re

# This is a graphical Gopher client in under 250 lines of code, implemented with Pituophis and PySimpleGUI for an interface. Pyperclip is used for the "Copy URL" feature.
# A tree is used for loading in menus, similar to the likes of WSGopher32 and Cyberdog. Backlinks are cut out, and menus are trimmed of blank selectors. Threaded binary downloads are supported as well.
# Based on the Chat interface example here: https://pysimplegui.trinket.io/demo-programs#/demo-programs/chat-instant-message-front-end

icons = {'1': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII=', 
         '0': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACRklEQVQ4jX3TvU8iQRgGcGorG5PNJlzOHImFxXXmSgu1pLYkFhbGFmta6Cn8U6ysbAzgfgwwM6y7sx8z67IgMuoq1XPNSSTovclTvr95JpMplf5No9HYbLfbRrvdNlqtltFqtYxGo2HU63WjXq8bZ2dnRq1WM2q1mnF6erpR+jyXl5cbhJDb0WgkP4dzLhljklIqh8OhJIRI27blzc3N7f7+/uYSaDabJudcBUGAKIoQRRHiOEaSJJBSrsVxnLRarZqlT/VNzrkKwxBxHMN1XXQ6HXS73bWkaQpCyNdAFEWQUsLzPDDGwDnHaDRaSZZl68DFxYXJOVdCCKRpin6/j16vB8uy1pLnOQgh6eHh4SrAGFNCCDw8PEAIAc/zcH9/D9/34fs+giBAEASYTqfrwPn5uUkpVUopZFkGSiksy4Jt23AcB67rghACQghms9n3QJqmGI/HCMMQvu9DCIE8zzGfz6G1htYa8/kcg8FgFTg5OTGHw6EKggB5nq8AYRiuPOvz8zP6/f4qcHx8bBJCVJIkmEwmiOMYQojlopQSSikopfD6+vo9kGUZJpMJOOfLOw8GA1BKwRgDYwxFUawD1WrVdF1XZVmG6XSKJEmW1T9OXywWWCwWXwMHBwc/er3e+KPB4+Mjnp6eoLXGy8sLiqLA+/s73t7eUBQFbNvO9/b2tpeAYRg/r66uPMuyZp1OR3e7XX13d6cty9KO42jXdZehlI6vr6+9ra2tysqP3NnZ2d7d3f1dqVT+/C9HR0flcrn862PvLwGSkDy9SoL4AAAAAElFTkSuQmCC', 
         '7': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACqUlEQVQ4jY2SXUhTYRjHn4pQtEJDGUU3dSV4U0hEV43uRlcl1oVd2Ae7KD+mJZUEnhzuhB+JLXaQdTbzuCMu54VG0XHfx2Q723Eed+bcmdOsdCOn6NRFmjvdSIjm6g/Pzfvw+/Hw5wXYlcbGRoler5d2d3dfRVH0zO592lAURbJj/vVP3kDK7vanRseDG3a7/XNbW1vOP2Gapm20J7CFGlyBN0PC5OuPQf6pbsTTRzFrHMetdXR05O0LDw4O1g97+C1VD8vNLawvRBeT8fB84isjxIVHuJvuG2JXaZqO7StwOOilZ7gtyghxYSa2+mX2e2I6HF3h2ak4qzTybxVqi9Pnn/yFouj5PTCCIHnOESZZrbFy3qlF/8TsMhuaTwxPfFs2U6NzpELHNt9usbx3jYVEg8FQt0eAomiuy+1NVr2yBCkuavEKC++4mSXSNh5TPiZ8d6txtu5Oi8Pk4UKiTqcr3yMQRfGAw+GIvyCd8XKt96UCZxUKLXvtPu6+WImz16twtvaJxuL0jQd+VlRUnPtrB11dXWVCOJKq1ph99zB3faWWvVWlZW9Uall5WbO5x8cLmwRBTO1bIgAARVF6IRxJYSZXrFZjZh5iFstzwhka9QspnudTnZ2dolKptKWVkCT5gGGYlYnJ0AYfDG1yHLdOEMQHkiSTJpNJVKvVokqlmk4rQRAkE0GQgoaGhgtyufwEABwsKSnJxzDsR29vr4hhmNjU1JQoKio6vJM7BACZAHAUAHIpiroUiURqwuFwTX9//2UAkGRlZZ1sb29fIklSHBgYEI1G45+PdXAHfBwAJMXFxQU4jss0Gs0VqVR6FgBOA8ApAJC0traGgsGgaLVaVwoLC4/sviIDALIB4BgA5ABA7vbkbL9lA0BGaWnpTZlMlp+2i//Nb4XAbVOmOUFgAAAAAElFTkSuQmCC',
         'h': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAC60lEQVQ4jYWTa0jTARTFb2grQijsW0kULfqW9sIia1ZkWVSmWRFhWUJqrexhoLMaFOTUMgktH/goclqW23y0NfO5Tc1tOififC7XKKnUzE3d+v9PX2JYjTyfz/lxufdcojkVvGBuz1+KFxbsyyySS4pK6npyimu7EkRSKf/Gs4srVwYu/G+Qy+UvKBLXNNU2GxiVthszMzOofqeCrNWCPJkeoqzX1qDTGRvdhgMDAz1lco21obULGm0njOYvqGvrhqrLCoV+GMrG9+jtG4SyrunnzmMJ2/4B5D1XvmIYBlNTU9C1G9BtHcOHcRYGix1KTTsmbTYwDAOr1Yr0zMIfXO6s3fj78326TQNOlmVRp2qF6fM0zOOAeRzosNjRqjeiuLIJFUo1+voHoNXqcDRSmOQCCO6Kjw8OWSBRNKGxdwL9o8DgGNAz4oTKaMGMwwGbzYbhj5+gbTfgtawaUXxhpwsgTHuR0qLvwlN5B6oMo2joncR7sx2a/gk064xgWRYsy8Jut+NVhQLil+U4fO6eiiicQ0REMQnFcQ9KtciXatDTb0bp2zaINZ9Q1GBBgUyDD8Mf8X3iB0ZGRqDV6XBB8BAhEaJ61wRHIlK3CvMbmTxpC1iWhcPhQJlCg5SyTgjFBlzNbUZW8RuYTCZUVb/BgeiHCD52+7EL4Od3ZsmlZJk+KVuJ0bExOJ1OfPk6irisesRmqhGRVovr919ArVYj80kuDkamTvP2Xtr5xxm3H0k8ESuqdCRnl2FoaAjZT8twUlSDsDtyBAsqcCoxFxKJBGf4Quw+GCdx16XVG4LO5ySlP2eq5Qrsu/YMu+LLwbtSiu2xheBFPUK84A627DlrIs+FPCLy/huwjIh2rPENyg6NFHwLu5rLHrqch/0xjxESnYHgEzcn/fxDaz08PMKJyJeI3D6ZNxGt53C8w3xWbL61btPhEr+AsPJVawMyvLyWRxMRj4jWENF8d+HZmkdEi34DlxLRYiLiuDP+AiIvzWJ84dNQAAAAAElFTkSuQmCC', 
         'i': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAJUlEQVQ4jWNgGAWjYBQME8D4//9/TkZGxu+kavz//z83AwODEQAPzAc8kOdqJQAAAABJRU5ErkJggg==', 
         '3': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACuklEQVQ4jX3T20pUcRQG8A8cpPZpcnSHmmZmhGVjBzTNiMxy//fM1OigXfUARVc9QvQMkQTdRFAg1E0lIlu0k5SlNZmZZzPMpnL27BkPeZi+LppMwVrw3a3fWjdrARtUl8tVNZSdfWVk5847IwUFtwezsi4/crmqNupdVy+A3eNeb6fj960sNTYwWV/HZKiei40NtE1jebSkpL0L2LUhHpVl75ejVZGfoRB/+nxMmiaTpsll0+SSaXJJCC7UBfmpony6Nz197zrcAuhTZQcnk2dOc+UPEoKLQvCHEFwQgvNCcE4Izgb8HCvdN2YBmasDhgsLbvwI+FfRHzAvBGeFYMIwGDcMOobBWG0to8JgOD+nCQBwE8icKjs0tWCaf7cIwYQQjAvxGwlBWwhGDYMzQvC7z8chb8nHZsCDTqD8W/VxzgYCTDQ1MW5ZjFsWnTWJtbUxZlmMWRaj164xEghw4shh3gf2o2vz5rMzp2roBIOMt7czkUisSywWo23btG2bjuMw2trKz8EgxyvL2ZGWVo9nLlfNtHGSM6EQnY6OVRiPx1fh2kzfusXR4mIOFBfRAo6hGdg2VFqSiBgGI34/pyoqOJGTwzG3myOaxmFN45Cm8YOqckBV+V5V+U5V2FuYG70L5KAZSO/Zkdc6rmdxVNM4kgKDqsoPKdCvKHynKOxTFIZlmWHPFj7epj+oBlwAAAs40leUPze4Zkt/CrxNodeyzF5ZZo8k8fn27MRDoGzdMT3V5Evh7bnLfZrGsCzzTQr1SBJfSRJfShJfyjK78rcudyrSxQ3P+bFbudBdkPv1te5hr2cLuxWF3bLM7gw3n+sePsnTI21u6fy/fmkTgKITQMP1DO3Bva2eiZY83b6fpzvNesbkVY/cWgmcA1AKQP/fU0oAcgHsOQBUlwI1ALwAdgDIAJC2tvkXFRyzrLKhFPAAAAAASUVORK5CYII=', 
         '9': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAC+0lEQVQ4jXVSX0gbBxz+tm7UIt2cL33pU0tf7MPc9jAGUgajb3kb+NI+CC10o+QhQ7YnEXTii4IpZEnUwD0UhRj1vJx3OfLv4sXsDAQ1eGpcjH849e6yIxcNadfBfn1ZS632e/6+D74/wAfg8XjaBUFQ4/H4kc/n6/wQ7xxCodADt9v9GQB4vd5v8vn8i62tLYpEIh4A6OnpaYlEIj9dEIbD4Svz8/OPFEX5JxqN/smy7G/pdHr14OCATNOkzc3NciaT8aqqmrJtm1Kp1HO32331nAnDMD9ns9lXGxsbpGka6bpOlmXR6ekpNZtNsm2bHMch0zRJFMVnl0YQBCGxt7dHx8fHZNs2NRoNchyH6vU62bZN1WqV8vn8Xm9vb+sF8cDAwN1CoVA3DIMcxyHDMHRZlseTyeTvOzs7a4Zh0NHREZVKJWIY5qnH42kHAIyPj3dyHMepqlqwLIvOzs6oWq3+t7Cw8Osb80AgcH91dXV/d3eXNE2jXC5XEwRhPRAI/IKpqaknlUqFarUaNZtNajQaVKlUzgYHB2+/M+k1SZJSxWKRVlZWaGlpiRKJBPn9/ikEg8HbsVjsD1VVs/V6nWq1GpmmSSzLDgWDwU8BwO/3/yjL8kkul6NMJkPhcHglFAr1jY6OfvW2A6/Xe2d7e/vUsiw6OTmhcrn8tyzLYVEUJwuFwl+KolA8HqdoNEoTExMPL11BUZS4rut0eHhIpVKJ1tfXSVVVkmWZYrEYsSxLHMe9GBsbu3dBPDc397RcLr/a39+nYrFIa2trtLy8TMlkkgRBIJ7naXFxkRKJBHEcVxgaGrpx7onpdPqJpmkveZ5PTU5ODs7MzGxIkvQvz/M0Ozur+3y+0MjIyANJknanp6fnLkvQ2tfX97itra0TwHcdHR0PGYbRRVGk/v7+GQD3AHS6XK7vAXwB4KP3Da4CuAHgDoCvW1pafhgeHs4yDGN1d3f3AvgWQAeAmwCuX1ri//gYwDUAn3d1dd1yuVxfAmgH0Argk/fJrwEaXuWjl/RWWwAAAABJRU5ErkJggg==',
         'I': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABNklEQVQ4jWNQtnE47NvUdYAcrGLjcJzBr7VrX9W56//Jwb5NXQeINiB314HTwgpKV0VVVG/n7z1ykWQD+GVlTzJAgYiS2j2KDBBWVnlAsgF5Ow+fEZJXuiiipHwzb+/RCyQbQFIghkyYsb/46Nm7ZBkQOWv+XgYGBncRJdUZ5ScvPUaWKzxw4lLlmas/cBqQsmbTEQYGhghoWLFJaOstrDh15WXVuev/wyfO3MPAxJRjkZC2qeLM1b8YBuTtPHyGiZ09hwEVcMmbWS6zTEzdzMDAYAwV0/CsbtyGYkDRoZPXuISEGhiwAz4GBgYRNDHL8Glzd/s2dR1gMAmPOSIgIzeJgYGBEYcBuICvpIbOdQYGBoZdDAwMLCRqhoGJDAwMDC1kamZgYGBoYGBgYFjLwMBQQyZeAwCR3MS3bOe39AAAAABJRU5ErkJggg==',
         'g': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABsUlEQVQ4ja2TTUsbURSG/SEttMY2m7rQKli6sIIrv9qJSZxMMr2TScebmBhc+EFLoBXLCMai1tAPbSkUuhKz6aZQiiLqQqR04cKlSUBwVcj8gKcLsWWSSRHaF57Nuee8vJd7blPT/5IwdXQzhmEJN6MGUVNDmDoNh+OPBAufbF4fLDG7NcPjr1kXohhAjY94G8QtgydrU4higN71TnoKt7m32u6ie7mNoBHwNtDMCN0v27nzvJWu2VsNURNhbwNrbJz9isNOqcpuucp+xWG37LBdctgqOXw7qVI8/ok1Me1tIJIZPvw4Y+37GbmVd0gpXcwsv0dKiWElXfVcLnduqMs0+b0yk4tvkVJSq4ta7ZmU8tzASKZZP6y4GmupNXIlSKQybByd1jVcOkEilWbzqMyzlTeXukJdAmGZFL5ssPj5I9P207r40ZSClJKHRsw9+HsPjBCThRDjS71kVu+SfdWBmPNzf+Iag1kfD6auo9ktKOEB72cMxvrQbB/qXDPq/BW0F1dR8z6G528wbPsJL/gJ5W+iRPob7IGpo4z0EdQGCUYvGPpDbAgl0v/3z/Qv+gW72bfPiU6yowAAAABJRU5ErkJggg==',
         'M': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACgElEQVQ4jY2TO0/bYBSGrbZbh6oLXZEYUlUZarAipAoJib3/gaVTGaqOXRg6IDFWghE1HVARU5cCQSStycVOsENNnNi52LG/OL7ks3MRioQEb5cWkSJEX+noLOd5zlkOw9yRnZ2dl/lsdiWb/blyfJx+u7q6+uiu2VtRVfUdpfQyiiIEQQDf99Go1zvJZHLqXliv1T6EYXjlui46nQ4sy4JhGDAMA7qu93ief3onXFGU977vX90EG40GNE2DqqqoVqsol2VnbW3tyS1YKhZf+75/ads2TNOcABVFQblcBs/zODk5QaGQq0zA6+vrU47jRKZpotlsQtf1P9vKyOVy0HUdrutiPB5DkiTIsoxUav/jtWB7a2u62yX9mlZDqVSCoihwHAfD4RAXFxc4Pz/HaDTCcDgEIQSqquLoKPV5QuC6TmTZFvr9PsbjMUajEQaDAfr9PsIwBKUUvV4PkiTBdV2kUv8IHKcTDQYDyKcymq0mPM+D67rXvdvtolgsot1uw3EcHBzsJW8JoihCGIY4TB8im88i/SONDJ9Bhs8gnUnj7OwM3W4XhBDs7d0QbG1uTtu2FfV6PQRBAK2uodVuwQ98EELQbDWRF/PQ6hoIIbAsC/v7379MCEzTjDzPg9E2EIYhPM+D4zjodDoghMC2bVSqFWi6dlvwZnl5tl7Xh57vgYZ0ArIsa6JaRgsto4Xd3a/fGIZ5yDAMwywuvuJEUSC/TuWeLJeoJJVoqVSkpaJIRVGkoihQQRCoIBSoUChQQRCCjY1P2wzDPP57xIOlpYUXC/Pzs4lEgkskWC7BshzLshzLxjk2Hufi8TgXj8e4WCzGzc3NPZ+ZeXb/Y/1PfgOxF0ZCQvJSWwAAAABJRU5ErkJggg==',  # mail/newsletter type, example here: gopher://rawtext.club/M/~cmccabe/pubnixhist/nixpub/1991-01-11
         'P': b'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',
         'cache': b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACu0lEQVQ4ja2SSUwTUBCGB8FYQZTEAydMuHjRi8STB2PEcJIWJAgCgikURYJsrUrYqoSKLJaWrexBgQIa6EJBoC0CLWCAllpaKIiRRRRZIxe98HuwGIV68yVfXl4y/5d5mSH6n4d/6xIjh+vnvUcB1/8XGXsEexels7z+KdDJC6MmxgaxYFFj0aqBuTcP4+0pmOhIhUHGg1HOg7Ez60cB18/NoWBcxW+wdD2Atfshpl+nYaY3Hba+DMyqMzGnycZ7LR8fBnKgV+b7ORTM64VLX8afYXWiGGsGEdaNYmyYSrH5rgxb5nJsT0mwbZFgfrRccCBcJYg8/WnyOVZM9Vgx1eOz/T7AZD2sg2XDBwSvJMnne6vCoCoJRKc4AEoRC8piJhTF/lAI/SEXXv1NpyTS/GfWiYgYubxrPrqmO9DWhkNTHQZ11Q28LGShNZ8JuSgQ3WVB6CoJhEocgK5K9l8dHCIiL78L3hcNMh5GpLEYbuJA3xiNtqJgyMQhUJSG4k19JPprI6CtCYe6IU67/wdePmc8L1t6sjEpT4axIwmG9ntQVkRBUR6BwRexeNsah1HpbQw3x0LXltq5X3DylOeJK7P9Atj6MjDTk46umlioqmPQXRMDZSUbQ83xMClSYJQlY6Q9TbpfcMiN4eI7P1S4u6h/goUhAab7sqFtTICuJRED0kTMabIxq86ErTcDYyp+naM1OPtxVLS7ZhTjq0GE1XEhrOrHGGjhYnk0H8sjT7E0nIdFnQBT6vxSRwKPZUPl9x1bHXZmavFtugbblipsmSXYNFdgw1SG9ckSrBnEsPYL8+zTIyIiFyJyJSKPR/dDfbOSw1i8u8EhiTGsyIRoJjuBw+QkcgI5KfFB7PSksJu5mezrCdHMc0R0jIgO7+2Bs/1xhIiOEpEbEbkT0XE77vaAKxEx7LXOROT0E4+/rF25GHCBAAAAAElFTkSuQmCC'
        }
icons['p'] = icons['I'] # pngs

texttypes = ['0', '1', '7', 'h', 'M']

# Regular expression to detect ANSI color codes
ANSI_COLOR_RE = re.compile(r'\033\[(\d+);(\d+);(\d+)m')

ANSI_COLORS = {
    (0, 0, 0): '#000000' ,  # Black
    (255, 191, 0): '#FFBF00',  # Amber
    (0, 255, 0): '#00FF00',   # Bright green
    (255, 255, 255): '#FFFFFF',  # White
    (0, 0, 255): '#0000FF',   # Blue
    (255, 0, 0): '#FF0000',   # Red
    (255, 255, 0): '#FFFF00', # Yellow
    # Add more colors as needed
}

def parse_ansi_colors(text):
    """
    Parses the text for ANSI color codes and splits it into segments.
    Each segment is a tuple (text, color) where color is a hex color code.
    """
    segments = []
    last_end = 0
    current_color = "#FFFFFF"  # Default color is white

    for match in ANSI_COLOR_RE.finditer(text):
        start, end = match.span()

        # Extract RGB from ANSI code and map to hex color
        rgb = tuple(int(match.group(i)) for i in range(1, 4))
        color = ANSI_COLORS.get(rgb, current_color)

        # Add text before this ANSI code with the current color
        if start > last_end:
            segments.append((text[last_end:start], current_color))

        # Update color and position
        current_color = color
        last_end = end

    # Add remaining text after last ANSI code
    if last_end < len(text):
        segments.append((text[last_end:], current_color))

    return segments

def display_text_with_colors(text):
    """
    Displays parsed text with colors applied. Clears the Multiline element
    and prints each segment in the respective color.
    """
    segments = parse_ansi_colors(text)
    window['-OUTPUT-'].update('')  # Clear output area

    # Print each segment in its designated color
    for segment, color in segments:
        window['-OUTPUT-'].print(segment, text_color=color, end='')


gophertree = sg.TreeData()

sg.theme('DarkTeal1')  # Add a touch of color

context_menu = ['', '&Copy URL']
text_menu = ['', ['&Save...', '&Copy File URL']]

gophermenu_layout = sg.Tree(data=gophertree, headings=[], change_submits=True,
                              auto_size_columns=True, num_rows=26, col0_width=115, max_col_width=200, key='_TREE_', show_expanded=True, enable_events=True, right_click_menu=context_menu, font='Consolas 10', background_color='#fff', text_color='#000')

plaintext_layout = sg.Multiline(key='-OUTPUT-', size=(35, 35), font=('Consolas 10'), background_color='#fff', right_click_menu=text_menu, autoscroll=False, disabled=True, metadata='', rstrip=False, wrap_lines=False)

layout = [[gophermenu_layout, plaintext_layout],
          [sg.Button('<'), sg.Input(size=(84, 5), key='-QUERY-', do_not_clear=True, default_text="gopher://gopherproject.org/1/", enable_events=True), sg.Button('Go'), sg.Button('Clear Cache'), sg.Checkbox('Use hierarchy', key='-USETREE-', default=True), sg.Text('...', key='-LOADING-', visible=False)],
           [sg.StatusBar(text='0 menus in cache.', key='-CACHE-'), sg.Text('', key='-DOWNLOADS-', visible=True, size=(60, 1))]]

window = sg.Window('TreeGopher', layout, font=('Segoe UI', ' 13'), default_button_element_size=(8, 1))

openNodes = []

cache = {}
loadedTextURL = ''

def trim_menu(menu):
    try:
        while menu[-1].text == '':
            del menu[-1]
    except:
        pass
    try:
        while menu[0].text == '':
            del menu[0]
    except:
        pass
    return menu

def populate(parentNode, request):
    global gophertree, openNodes

    window.find_element('-QUERY-').update(request.url())
    window.find_element('-LOADING-').update(visible=True)

    if not parentNode in openNodes:
        passes = 0
        from_cache = False
        try:
            if request.url() in cache:
                from_cache = True
                resp = cache[request.url()]
            else:
                resp = request.get()
                cache[request.url()] = resp
            passes += 1
        except:
            sg.popup("We're sorry!", request.url() + ' could not be fetched. Try again later.')
        if passes == 1:
            try:
                menu = trim_menu(resp.menu())
                passes += 1
            except:
                sg.popup("We're sorry!", request.url() + ' could not be parsed as a menu for one reason or another.')
        if passes == 2:
            if from_cache:
                gophertree.insert(parentNode, request.url() + ' <cached>', text='- This is a cached menu, double click to go to the live version -', values=[], icon=icons['cache'])
            for item in menu:
                if not item.request().url() in openNodes:
                    sub_url = item.request().url()
                    if item.path.startswith("URL:"):
                        sub_url = item.path[4:]
                    if item.type in icons:
                        icon = icons[item.type]
                    else:
                        icon = icons['9']
                    if item.type == 'i':
                        gophertree.insert(parentNode, sub_url,
                                          text=item.text, values=[], icon=icon)
                    else:
                        gophertree.insert(parentNode, sub_url, text=item.text, values=[
                            sub_url], icon=icon)

            openNodes.append(parentNode)

            window.find_element('_TREE_').Update(gophertree)

    window.find_element('-LOADING-').update(visible=False)

gui_queue = queue.Queue()

def download_thread(req, dlpath, gui_queue):     # This uses Pituophis' Request().stream() function to download a file chunks at a time (instead of all in one shot like with .get())
    with open(dlpath, "wb") as dl:
        remote_file = req.stream().makefile('rb')
        while True:
            piece = remote_file.read(1024)  
            if not piece:
                break
            dl.write(piece)
    gui_queue.put(dlpath)  # put a message into queue for GUI

history = []

def dlPopup(url):
    return sg.popup_get_file('Where to save this file?', 'Download {}'.format(
            url), default_path=url.split('/')[-1], save_as=True)

def go(url):
    global gophertree, openNodes, loadedTextURL

    window['-LOADING-'].update(visible=True)

    # Parse the Gopher URL
    req = gopher.parse_url(url)
    window['-QUERY-'].update(req.url())

    # Check if the request type is one of the text-based types
    if req.type in texttypes:
        if req.type in ['1', '7']:  # Handle menu-based types (directories)
            gophertree = sg.TreeData()
            gophertree.insert('', key=req.url(), text=req.url(),
                              values=[req.url()], icon=icons[req.type])
            parentNode = req.url()
            history.append(req.url())
            openNodes = []
            populate(parentNode, req)
        else:  # Handle content-based types (e.g., plain text)
            try:
                # Retrieve the response content
                resp = req.get()
                loadedTextURL = req.url()

                # Display text with ANSI colors applied
                display_text_with_colors(resp.text())
            except Exception as e:
                sg.popup("We're sorry!", f"{req.url()} could not be fetched. Try again later.\nError: {e}")
    else:
        # For binary or downloadable files, prompt user to save the file
        dlpath = dlPopup(req.url())
        if dlpath:
            window['-DOWNLOADS-'].update(f'Downloading {dlpath}')
            threading.Thread(target=download_thread, args=(req, dlpath, gui_queue), daemon=True).start()

    # Hide the loading indicator once done
    window['-LOADING-'].update(visible=False)



def plural(x):
    if x > 1 or x < 1: 
        return 's'
    return ''

previousvalue = None

while True:     # The Event Loop
    event, value = window.read()
    if event in (None, 'Exit'):            # quit if exit button or X
        break
    elif event == '_TREE_':
        if value == previousvalue:
            previousevent = None
            # DOUBLE CLICK
            # TODO: cooldown
            window.find_element('-LOADING-').update(visible=True)

            url = value['_TREE_'][0]

            if url.endswith(' <cached>'):
                url = url[:-9]
                del cache[url]
                go(url)
            else:
                if url.startswith('gopher'):
                    req = gopher.parse_url(url)
                    if req.type == '1':
                        parentNode = url
                        if value['-USETREE-']:
                            populate(parentNode, req)
                        else:
                            go(parentNode)
                    elif req.type == '7':
                        q = sg.popup_get_text('Search on ' + req.host, '')
                        if not q is None:
                            req.query = q
                            go(req.url())
                    elif req.type != 'i':
                        go(req.url())

                    window.find_element('-LOADING-').update(visible=False)
                else:
                    os.startfile(url)
        previousvalue = value
    elif event == 'Go':
        go(value['-QUERY-'].rstrip())
    elif event == '<':
        if len(history) > 1:
            h = history[-2]
            history.remove(h)
            history.remove(history[-1])
            go(h)
    elif event == 'Copy URL':
        url = value['_TREE_'][0]
        if url.endswith(' <cached>'):
                url = url[:-9]
        pyperclip.copy(url)
    elif event == 'Copy File URL':
        pyperclip.copy(loadedTextURL)
    elif event == 'Save...':
        dlpath = dlPopup(loadedTextURL)
        if not dlpath is None:
            with open(dlpath, 'w') as f:
                f.write(value['-OUTPUT-'])

    elif event == 'Clear Cache':
        cache = {}
    try:
        message = gui_queue.get_nowait()
    except queue.Empty:             # get_nowait() will get exception when Queue is empty
        message = None              # break from the loop if no more messages are queued up
    # if message received from queue, display the message in the Window
    if message:
        window.find_element('-DOWNLOADS-').update(value='')
        if sg.popup_yes_no('Finished downloading {}. Would you like to open the downloaded file?'.format(message)):
            os.startfile(message)
    window.find_element('-CACHE-').update(value='{} menu{} in cache.'.format(len(cache), plural(len(cache))))
window.close()