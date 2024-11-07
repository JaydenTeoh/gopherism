import asyncio
import glob
import urllib
import http.server
from threading import Thread
import mimetypes
import os
import re
import socket
import ssl
from operator import itemgetter
from os.path import realpath
from urllib.parse import urlparse

from natsort import natsorted

mimetypes.add_type('application/pdf', '.pdf')

icons = {'1': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII=', 
         '0': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACRklEQVQ4jX3TvU8iQRgGcGorG5PNJlzOHImFxXXmSgu1pLYkFhbGFmta6Cn8U6ysbAzgfgwwM6y7sx8z67IgMuoq1XPNSSTovclTvr95JpMplf5No9HYbLfbRrvdNlqtltFqtYxGo2HU63WjXq8bZ2dnRq1WM2q1mnF6erpR+jyXl5cbhJDb0WgkP4dzLhljklIqh8OhJIRI27blzc3N7f7+/uYSaDabJudcBUGAKIoQRRHiOEaSJJBSrsVxnLRarZqlT/VNzrkKwxBxHMN1XXQ6HXS73bWkaQpCyNdAFEWQUsLzPDDGwDnHaDRaSZZl68DFxYXJOVdCCKRpin6/j16vB8uy1pLnOQgh6eHh4SrAGFNCCDw8PEAIAc/zcH9/D9/34fs+giBAEASYTqfrwPn5uUkpVUopZFkGSiksy4Jt23AcB67rghACQghms9n3QJqmGI/HCMMQvu9DCIE8zzGfz6G1htYa8/kcg8FgFTg5OTGHw6EKggB5nq8AYRiuPOvz8zP6/f4qcHx8bBJCVJIkmEwmiOMYQojlopQSSikopfD6+vo9kGUZJpMJOOfLOw8GA1BKwRgDYwxFUawD1WrVdF1XZVmG6XSKJEmW1T9OXywWWCwWXwMHBwc/er3e+KPB4+Mjnp6eoLXGy8sLiqLA+/s73t7eUBQFbNvO9/b2tpeAYRg/r66uPMuyZp1OR3e7XX13d6cty9KO42jXdZehlI6vr6+9ra2tysqP3NnZ2d7d3f1dqVT+/C9HR0flcrn862PvLwGSkDy9SoL4AAAAAElFTkSuQmCC', 
         '7': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACqUlEQVQ4jY2SXUhTYRjHn4pQtEJDGUU3dSV4U0hEV43uRlcl1oVd2Ae7KD+mJZUEnhzuhB+JLXaQdTbzuCMu54VG0XHfx2Q723Eed+bcmdOsdCOn6NRFmjvdSIjm6g/Pzfvw+/Hw5wXYlcbGRoler5d2d3dfRVH0zO592lAURbJj/vVP3kDK7vanRseDG3a7/XNbW1vOP2Gapm20J7CFGlyBN0PC5OuPQf6pbsTTRzFrHMetdXR05O0LDw4O1g97+C1VD8vNLawvRBeT8fB84isjxIVHuJvuG2JXaZqO7StwOOilZ7gtyghxYSa2+mX2e2I6HF3h2ak4qzTybxVqi9Pnn/yFouj5PTCCIHnOESZZrbFy3qlF/8TsMhuaTwxPfFs2U6NzpELHNt9usbx3jYVEg8FQt0eAomiuy+1NVr2yBCkuavEKC++4mSXSNh5TPiZ8d6txtu5Oi8Pk4UKiTqcr3yMQRfGAw+GIvyCd8XKt96UCZxUKLXvtPu6+WImz16twtvaJxuL0jQd+VlRUnPtrB11dXWVCOJKq1ph99zB3faWWvVWlZW9Uall5WbO5x8cLmwRBTO1bIgAARVF6IRxJYSZXrFZjZh5iFstzwhka9QspnudTnZ2dolKptKWVkCT5gGGYlYnJ0AYfDG1yHLdOEMQHkiSTJpNJVKvVokqlmk4rQRAkE0GQgoaGhgtyufwEABwsKSnJxzDsR29vr4hhmNjU1JQoKio6vJM7BACZAHAUAHIpiroUiURqwuFwTX9//2UAkGRlZZ1sb29fIklSHBgYEI1G45+PdXAHfBwAJMXFxQU4jss0Gs0VqVR6FgBOA8ApAJC0traGgsGgaLVaVwoLC4/sviIDALIB4BgA5ABA7vbkbL9lA0BGaWnpTZlMlp+2i//Nb4XAbVOmOUFgAAAAAElFTkSuQmCC',
         'h': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAC60lEQVQ4jYWTa0jTARTFb2grQijsW0kULfqW9sIia1ZkWVSmWRFhWUJqrexhoLMaFOTUMgktH/goclqW23y0NfO5Tc1tOififC7XKKnUzE3d+v9PX2JYjTyfz/lxufdcojkVvGBuz1+KFxbsyyySS4pK6npyimu7EkRSKf/Gs4srVwYu/G+Qy+UvKBLXNNU2GxiVthszMzOofqeCrNWCPJkeoqzX1qDTGRvdhgMDAz1lco21obULGm0njOYvqGvrhqrLCoV+GMrG9+jtG4SyrunnzmMJ2/4B5D1XvmIYBlNTU9C1G9BtHcOHcRYGix1KTTsmbTYwDAOr1Yr0zMIfXO6s3fj78326TQNOlmVRp2qF6fM0zOOAeRzosNjRqjeiuLIJFUo1+voHoNXqcDRSmOQCCO6Kjw8OWSBRNKGxdwL9o8DgGNAz4oTKaMGMwwGbzYbhj5+gbTfgtawaUXxhpwsgTHuR0qLvwlN5B6oMo2joncR7sx2a/gk064xgWRYsy8Jut+NVhQLil+U4fO6eiiicQ0REMQnFcQ9KtciXatDTb0bp2zaINZ9Q1GBBgUyDD8Mf8X3iB0ZGRqDV6XBB8BAhEaJ61wRHIlK3CvMbmTxpC1iWhcPhQJlCg5SyTgjFBlzNbUZW8RuYTCZUVb/BgeiHCD52+7EL4Od3ZsmlZJk+KVuJ0bExOJ1OfPk6irisesRmqhGRVovr919ArVYj80kuDkamTvP2Xtr5xxm3H0k8ESuqdCRnl2FoaAjZT8twUlSDsDtyBAsqcCoxFxKJBGf4Quw+GCdx16XVG4LO5ySlP2eq5Qrsu/YMu+LLwbtSiu2xheBFPUK84A627DlrIs+FPCLy/huwjIh2rPENyg6NFHwLu5rLHrqch/0xjxESnYHgEzcn/fxDaz08PMKJyJeI3D6ZNxGt53C8w3xWbL61btPhEr+AsPJVawMyvLyWRxMRj4jWENF8d+HZmkdEi34DlxLRYiLiuDP+AiIvzWJ84dNQAAAAAElFTkSuQmCC', 
         'i': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAJUlEQVQ4jWNgGAWjYBQME8D4//9/TkZGxu+kavz//z83AwODEQAPzAc8kOdqJQAAAABJRU5ErkJggg==', 
         '3': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACuklEQVQ4jX3T20pUcRQG8A8cpPZpcnSHmmZmhGVjBzTNiMxy//fM1OigXfUARVc9QvQMkQTdRFAg1E0lIlu0k5SlNZmZZzPMpnL27BkPeZi+LppMwVrw3a3fWjdrARtUl8tVNZSdfWVk5847IwUFtwezsi4/crmqNupdVy+A3eNeb6fj960sNTYwWV/HZKiei40NtE1jebSkpL0L2LUhHpVl75ejVZGfoRB/+nxMmiaTpsll0+SSaXJJCC7UBfmpony6Nz197zrcAuhTZQcnk2dOc+UPEoKLQvCHEFwQgvNCcE4Izgb8HCvdN2YBmasDhgsLbvwI+FfRHzAvBGeFYMIwGDcMOobBWG0to8JgOD+nCQBwE8icKjs0tWCaf7cIwYQQjAvxGwlBWwhGDYMzQvC7z8chb8nHZsCDTqD8W/VxzgYCTDQ1MW5ZjFsWnTWJtbUxZlmMWRaj164xEghw4shh3gf2o2vz5rMzp2roBIOMt7czkUisSywWo23btG2bjuMw2trKz8EgxyvL2ZGWVo9nLlfNtHGSM6EQnY6OVRiPx1fh2kzfusXR4mIOFBfRAo6hGdg2VFqSiBgGI34/pyoqOJGTwzG3myOaxmFN45Cm8YOqckBV+V5V+U5V2FuYG70L5KAZSO/Zkdc6rmdxVNM4kgKDqsoPKdCvKHynKOxTFIZlmWHPFj7epj+oBlwAAAs40leUPze4Zkt/CrxNodeyzF5ZZo8k8fn27MRDoGzdMT3V5Evh7bnLfZrGsCzzTQr1SBJfSRJfShJfyjK78rcudyrSxQ3P+bFbudBdkPv1te5hr2cLuxWF3bLM7gw3n+sePsnTI21u6fy/fmkTgKITQMP1DO3Bva2eiZY83b6fpzvNesbkVY/cWgmcA1AKQP/fU0oAcgHsOQBUlwI1ALwAdgDIAJC2tvkXFRyzrLKhFPAAAAAASUVORK5CYII=', 
         '9': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAC+0lEQVQ4jXVSX0gbBxz+tm7UIt2cL33pU0tf7MPc9jAGUgajb3kb+NI+CC10o+QhQ7YnEXTii4IpZEnUwD0UhRj1vJx3OfLv4sXsDAQ1eGpcjH849e6yIxcNadfBfn1ZS632e/6+D74/wAfg8XjaBUFQ4/H4kc/n6/wQ7xxCodADt9v9GQB4vd5v8vn8i62tLYpEIh4A6OnpaYlEIj9dEIbD4Svz8/OPFEX5JxqN/smy7G/pdHr14OCATNOkzc3NciaT8aqqmrJtm1Kp1HO32331nAnDMD9ns9lXGxsbpGka6bpOlmXR6ekpNZtNsm2bHMch0zRJFMVnl0YQBCGxt7dHx8fHZNs2NRoNchyH6vU62bZN1WqV8vn8Xm9vb+sF8cDAwN1CoVA3DIMcxyHDMHRZlseTyeTvOzs7a4Zh0NHREZVKJWIY5qnH42kHAIyPj3dyHMepqlqwLIvOzs6oWq3+t7Cw8Osb80AgcH91dXV/d3eXNE2jXC5XEwRhPRAI/IKpqaknlUqFarUaNZtNajQaVKlUzgYHB2+/M+k1SZJSxWKRVlZWaGlpiRKJBPn9/ikEg8HbsVjsD1VVs/V6nWq1GpmmSSzLDgWDwU8BwO/3/yjL8kkul6NMJkPhcHglFAr1jY6OfvW2A6/Xe2d7e/vUsiw6OTmhcrn8tyzLYVEUJwuFwl+KolA8HqdoNEoTExMPL11BUZS4rut0eHhIpVKJ1tfXSVVVkmWZYrEYsSxLHMe9GBsbu3dBPDc397RcLr/a39+nYrFIa2trtLy8TMlkkgRBIJ7naXFxkRKJBHEcVxgaGrpx7onpdPqJpmkveZ5PTU5ODs7MzGxIkvQvz/M0Ozur+3y+0MjIyANJknanp6fnLkvQ2tfX97itra0TwHcdHR0PGYbRRVGk/v7+GQD3AHS6XK7vAXwB4KP3Da4CuAHgDoCvW1pafhgeHs4yDGN1d3f3AvgWQAeAmwCuX1ri//gYwDUAn3d1dd1yuVxfAmgH0Argk/fJrwEaXuWjl/RWWwAAAABJRU5ErkJggg==',
         'I': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABNklEQVQ4jWNQtnE47NvUdYAcrGLjcJzBr7VrX9W56//Jwb5NXQeINiB314HTwgpKV0VVVG/n7z1ykWQD+GVlTzJAgYiS2j2KDBBWVnlAsgF5Ow+fEZJXuiiipHwzb+/RCyQbQFIghkyYsb/46Nm7ZBkQOWv+XgYGBncRJdUZ5ScvPUaWKzxw4lLlmas/cBqQsmbTEQYGhghoWLFJaOstrDh15WXVuev/wyfO3MPAxJRjkZC2qeLM1b8YBuTtPHyGiZ09hwEVcMmbWS6zTEzdzMDAYAwV0/CsbtyGYkDRoZPXuISEGhiwAz4GBgYRNDHL8Glzd/s2dR1gMAmPOSIgIzeJgYGBEYcBuICvpIbOdQYGBoZdDAwMLCRqhoGJDAwMDC1kamZgYGBoYGBgYFjLwMBQQyZeAwCR3MS3bOe39AAAAABJRU5ErkJggg==',
         'g': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABsUlEQVQ4ja2TTUsbURSG/SEttMY2m7rQKli6sIIrv9qJSZxMMr2TScebmBhc+EFLoBXLCMai1tAPbSkUuhKz6aZQiiLqQqR04cKlSUBwVcj8gKcLsWWSSRHaF57Nuee8vJd7blPT/5IwdXQzhmEJN6MGUVNDmDoNh+OPBAufbF4fLDG7NcPjr1kXohhAjY94G8QtgydrU4higN71TnoKt7m32u6ie7mNoBHwNtDMCN0v27nzvJWu2VsNURNhbwNrbJz9isNOqcpuucp+xWG37LBdctgqOXw7qVI8/ok1Me1tIJIZPvw4Y+37GbmVd0gpXcwsv0dKiWElXfVcLnduqMs0+b0yk4tvkVJSq4ta7ZmU8tzASKZZP6y4GmupNXIlSKQybByd1jVcOkEilWbzqMyzlTeXukJdAmGZFL5ssPj5I9P207r40ZSClJKHRsw9+HsPjBCThRDjS71kVu+SfdWBmPNzf+Iag1kfD6auo9ktKOEB72cMxvrQbB/qXDPq/BW0F1dR8z6G528wbPsJL/gJ5W+iRPob7IGpo4z0EdQGCUYvGPpDbAgl0v/3z/Qv+gW72bfPiU6yowAAAABJRU5ErkJggg==',
         'M': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACgElEQVQ4jY2TO0/bYBSGrbZbh6oLXZEYUlUZarAipAoJib3/gaVTGaqOXRg6IDFWghE1HVARU5cCQSStycVOsENNnNi52LG/OL7ks3MRioQEb5cWkSJEX+noLOd5zlkOw9yRnZ2dl/lsdiWb/blyfJx+u7q6+uiu2VtRVfUdpfQyiiIEQQDf99Go1zvJZHLqXliv1T6EYXjlui46nQ4sy4JhGDAMA7qu93ief3onXFGU977vX90EG40GNE2DqqqoVqsol2VnbW3tyS1YKhZf+75/ads2TNOcABVFQblcBs/zODk5QaGQq0zA6+vrU47jRKZpotlsQtf1P9vKyOVy0HUdrutiPB5DkiTIsoxUav/jtWB7a2u62yX9mlZDqVSCoihwHAfD4RAXFxc4Pz/HaDTCcDgEIQSqquLoKPV5QuC6TmTZFvr9PsbjMUajEQaDAfr9PsIwBKUUvV4PkiTBdV2kUv8IHKcTDQYDyKcymq0mPM+D67rXvdvtolgsot1uw3EcHBzsJW8JoihCGIY4TB8im88i/SONDJ9Bhs8gnUnj7OwM3W4XhBDs7d0QbG1uTtu2FfV6PQRBAK2uodVuwQ98EELQbDWRF/PQ6hoIIbAsC/v7379MCEzTjDzPg9E2EIYhPM+D4zjodDoghMC2bVSqFWi6dlvwZnl5tl7Xh57vgYZ0ArIsa6JaRgsto4Xd3a/fGIZ5yDAMwywuvuJEUSC/TuWeLJeoJJVoqVSkpaJIRVGkoihQQRCoIBSoUChQQRCCjY1P2wzDPP57xIOlpYUXC/Pzs4lEgkskWC7BshzLshzLxjk2Hufi8TgXj8e4WCzGzc3NPZ+ZeXb/Y/1PfgOxF0ZCQvJSWwAAAABJRU5ErkJggg==',  # mail/newsletter type, example here: gopher://rawtext.club/M/~cmccabe/pubnixhist/nixpub/1991-01-11
         'P': 'data:image/png;base64,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',
         'cache': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACu0lEQVQ4ja2SSUwTUBCGB8FYQZTEAydMuHjRi8STB2PEcJIWJAgCgikURYJsrUrYqoSKLJaWrexBgQIa6EJBoC0CLWCAllpaKIiRRRRZIxe98HuwGIV68yVfXl4y/5d5mSH6n4d/6xIjh+vnvUcB1/8XGXsEexels7z+KdDJC6MmxgaxYFFj0aqBuTcP4+0pmOhIhUHGg1HOg7Ez60cB18/NoWBcxW+wdD2Atfshpl+nYaY3Hba+DMyqMzGnycZ7LR8fBnKgV+b7ORTM64VLX8afYXWiGGsGEdaNYmyYSrH5rgxb5nJsT0mwbZFgfrRccCBcJYg8/WnyOVZM9Vgx1eOz/T7AZD2sg2XDBwSvJMnne6vCoCoJRKc4AEoRC8piJhTF/lAI/SEXXv1NpyTS/GfWiYgYubxrPrqmO9DWhkNTHQZ11Q28LGShNZ8JuSgQ3WVB6CoJhEocgK5K9l8dHCIiL78L3hcNMh5GpLEYbuJA3xiNtqJgyMQhUJSG4k19JPprI6CtCYe6IU67/wdePmc8L1t6sjEpT4axIwmG9ntQVkRBUR6BwRexeNsah1HpbQw3x0LXltq5X3DylOeJK7P9Atj6MjDTk46umlioqmPQXRMDZSUbQ83xMClSYJQlY6Q9TbpfcMiN4eI7P1S4u6h/goUhAab7sqFtTICuJRED0kTMabIxq86ErTcDYyp+naM1OPtxVLS7ZhTjq0GE1XEhrOrHGGjhYnk0H8sjT7E0nIdFnQBT6vxSRwKPZUPl9x1bHXZmavFtugbblipsmSXYNFdgw1SG9ckSrBnEsPYL8+zTIyIiFyJyJSKPR/dDfbOSw1i8u8EhiTGsyIRoJjuBw+QkcgI5KfFB7PSksJu5mezrCdHMc0R0jIgO7+2Bs/1xhIiOEpEbEbkT0XE77vaAKxEx7LXOROT0E4+/rF25GHCBAAAAAElFTkSuQmCC',
         'default': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAJUlEQVQ4jWNgGAWjYBQME8D4//9/TkZGxu+kavz//z83AwODEQAPzAc8kOdqJQAAAABJRU5ErkJggg==', 
        }


class Response:
    """
    *Client.* Returned by Request.get() and get(). Represents a received binary object from a Gopher server.
    """

    def __init__(self, stream):
        """
        Reads a BufferedReader to the object's binary property and initializes a new Response object.
        """
        self.binary = stream.read()
        """
        The data received from the server as a Bytes binary object.
        """

    def text(self):
        """
        Returns the binary decoded as a UTF-8 String.
        """
        return self.binary.decode('utf-8')

    def menu(self):
        """
        Decodes the binary as UTF-8 text and parses it as a Gopher menu. Returns a List of Gopher menu items parsed as the Item type.
        """
        return parse_menu(self.binary.decode('utf-8'))


class Request:
    """
    *Client/Server.* Represents a request to be sent to a Gopher server, or received from a client.
    """

    def __init__(self, host='127.0.0.1', port=70,
                 advertised_port=None, path='/', query='',
                 itype='9', tls=False, tls_verify=True, client='',
                 pub_dir='pub/', alt_handler=False):
        """
        Initializes a new Request object.
        """
        self.host = str(host)
        """
        *Client/Server.* The hostname of the server.
        """
        self.port = int(port)
        """
        *Client/Server.* The port of the server. For regular Gopher servers, this is most commonly 70, 
        and for S/Gopher servers it is typically 105.
        """
        if advertised_port is None:
            advertised_port = self.port

        self.advertised_port = int(advertised_port)
        """
        *Server.* Used by the default handler. Set this if the server itself
        is being hosted on another port than the advertised port (like port 70), with
        a firewall or some other software rerouting that port to the server's real port. 
        """
        self.path = str(path)
        """
        *Client/Server.* The selector string to request, or being requested.
        """
        self.query = str(query)
        """
        *Client/Server.* Search query for the server to process. Omitted when blank.
        """
        self.type = str(itype)
        """
        *Client.* Item type of the request. Purely for client-side usage, not used when sending or receiving requests.
        """
        self.tls = tls
        """
        *Client/Server.* Whether the request is to be, or was sent to an S/Gopher server over TLS.
        """
        self.tls_verify = tls_verify
        """
        *Client.* Whether to verify the certificate sent from the server, rejecting self-signed and invalid certificates.
        """
        self.client = str(client)  # only used in server
        """
        *Server.* The IP address of the connected client.
        """
        self.pub_dir = str(pub_dir)  # only used in server
        """
        *Server.* The default handler uses this as which directory to serve. Default is 'pub/'.
        """
        self.alt_handler = alt_handler

    def stream(self):
        """
        *Client.* Lower-level fetching. Sends the request and returns a BufferedReader.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.host.count(':') > 1:
            # ipv6
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        if self.tls:
            context = ssl._create_unverified_context()
            if self.tls_verify:  # TODO: for some reason this is always true when using the get() shorthand
                context = ssl.create_default_context()
            s = context.wrap_socket(s, server_hostname=self.host)
        else:
            s.settimeout(10.0)
        s.connect((self.host.replace('[', '').replace(']', ''),
                   int(self.port)))
        if self.query == '':
            msg = self.path + '\r\n'
        else:
            msg = self.path + '\t' + self.query + '\r\n'
        s.sendall(msg.encode('utf-8'))
        return s

    def get(self):
        """
        *Client.* Sends the request and returns a Response object.
        """
        return Response(self.stream().makefile('rb'))

    def url(self):
        """
        Returns a URL equivalent to the Request's properties.
        """
        protocol = 'gopher'
        if self.tls:
            protocol = 'gophers'
        path = self.path
        query = ''
        if not (self.query == ''):
            query = '%09' + self.query
        hst = self.host
        if not self.port == 70:
            hst += ':{}'.format(self.port)
        return '{}://{}/{}{}{}'.format(protocol, hst, self.type, path, query)


class Item:
    """
    *Server/Client.* Represents an item in a Gopher menu.
    """

    def __init__(self, itype='i', text='', path='/', host='', port=0, tls=False):
        """
        Initializes a new Item object.
        """
        self.type = itype
        """
        The type of item.
        """
        self.text = text
        """
        The name, or text that is displayed when the item is in a menu.
        """
        self.path = path
        """
        Where the item links to on the target server.
        """
        self.host = host
        """
        The hostname of the target server.
        """
        self.port = port
        """
        The port of the target server. For regular Gopher servers, this is most commonly 70, 
        and for S/Gopher servers it is typically 105.
        """
        self.tls = tls
        """
        True if the item leads to an S/Gopher server with TLS enabled.
        """

    def source(self):
        """
        Returns the item as a line in a Gopher menu.
        """
        port = int(self.port)
        if self.tls:
            # Add digits to display that this is a TLS item
            while len(str(port)) < 5:
                port = '0' + str(port)
            port = '1' + str(port)
            port = int(port)
        return str(self.type) + str(self.text) + '\t' + str(self.path) + '\t' + str(self.host) + '\t' + str(
            port) + '\r\n'

    def request(self):
        """
        Returns a Request to where the item leads.
        """
        req = Request()
        req.type = self.type
        req.host = self.host
        req.port = self.port
        req.path = self.path
        req.tls = self.tls
        return req


def parse_menu(source):
    """
    *Client.* Parses a String as a Gopher menu. Returns a List of Items.
    """
    parsed_menu = []
    menu = source.replace('\r\n', '\n').replace('\n', '\r\n').split('\r\n')
    for line in menu:
        item = Item()
        if line.startswith('i'):
            item.type = 'i'
            item.text = line[1:].split('\t')[0]
            item.path = '/'
            item.host = ''
            item.port = 0
        else:
            line = line.split('\t')
            while len(
                    line) > 4:  # discard Gopher+ and other naughty stuff
                line = line[:-1]
            line = '\t'.join(line)
            matches = re.match(r'^(.)(.*)\t(.*)\t(.*)\t(.*)', line)
            if matches:
                item.type = matches[1]
                item.text = matches[2]
                item.path = matches[3]
                item.host = matches[4]
                item.port = matches[5]
                try:
                    item.port = int(item.port)
                except:
                    item.port = 70
                # detect TLS
                if item.port > 65535:
                    item.tls = True
                    # typically the port is sent as 100105
                    # remove first number to get at 5 digits
                    item.port = int(str(item.port)[1:])
        parsed_menu.append(item)
    return parsed_menu


def parse_url(url):
    """
    *Client.* Parses a Gopher URL and returns an equivalent Request.
    """
    req = Request(host='', port=70, path='/', query='', tls=False)

    up = urlparse(url)

    if up.scheme == '':
        up = urlparse('gopher://' + url)

    if up.scheme == 'gophers':
        req.tls = True

    req.path = up.path
    if up.query:
        req.path += '?{}'.format(up.query)  # NOT to be confused with actual gopher queries, which use %09
                                            # this just combines them back into one string
    req.host = up.hostname
    req.port = up.port
    if up.port is None:
        req.port = 70
    if req.path:
        if req.path.endswith('/'):
            req.type = '1'
        if len(req.path) > 1:
            req.type = req.path[1]
        req.path = req.path[2:]
    else:
        req.type = '1'

    if '%09' in req.path:       # handle gopher queries
        req.query = ''.join(req.path.split('%09')[1:])
        req.path = req.path.split('%09')[0]

    return req


def get(host, port=70, path='/', query='', tls=False, tls_verify=True):
    """
    *Client.* Quickly creates and sends a Request. Returns a Response object.
    """
    req = Request(host=host, port=port, path=path,
                  query=query, tls=tls, tls_verify=tls_verify)
    if '/' in host or ':' in host:
        req = parse_url(host)
    return req.get()


# Server stuff
mime_starts_with = {
    'image': 'I',
    'text': '0',
    'audio/x-wav': 's',
    'image/gif': 'g',
    'text/html': 'h',
    'application/pdf': 'P'
}

errors = {
    '404': Item(itype='3', text='404: {} does not exist.'),
    '403': Item(itype='3', text='403: Resource outside of publish directory.'),
    '403_glob': Item(itype='3', text='403: Gopher glob is out of scope.'),
    'no_pub_dir': Item(itype='3', text='500: Publish directory does not exist.')
}


def parse_gophermap(source, def_host='127.0.0.1', def_port='70',
                    gophermap_dir='/', pub_dir='pub/', tls=False):
    """
    *Server.* Converts a Bucktooth-style Gophermap (as a String or List) into a Gopher menu as a List of Items to send.
    """
    if not gophermap_dir.endswith('/'):
        gophermap_dir += '/'
    if not pub_dir.endswith('/'):
        pub_dir += '/'

    if type(source) == str:
        source = source.replace('\r\n', '\n').split('\n')
    new_menu = []
    for item in source:
        if '\t' in item:
            # this is not information
            item = item.split('\t')
            expanded = False
            # 1Text    pictures/    host.host    port
            #  ^           ^           ^           ^
            itype = item[0][0]
            text = item[0][1:]
            path = gophermap_dir + text
            if itype == '1':
                path += '/'
            host = def_host
            port = def_port

            if len(item) > 1:
                path = item[1]
            if len(item) > 2:
                host = item[2]
            if len(item) > 3:
                port = item[3]

            if path == '':
                path = gophermap_dir + text
                if itype == '1':
                    path += '/'

            if not path.startswith('URL:'):
                # fix relative path
                if not path.startswith('/'):
                    path = realpath(gophermap_dir + '/' + path)

                # globbing
                if '*' in path:
                    expanded = True
                    if os.path.abspath(pub_dir) in os.path.abspath(
                            pub_dir + path):
                        g = natsorted(glob.glob(pub_dir + path))

                        listing = []

                        for file in g:
                            file = re.sub(
                                r'/{2}', r'/', file).replace('\\', '/')
                            s = Item()
                            s.type = itype
                            if s.type == '?':
                                s.type = '9'
                                if path.startswith('URL:'):
                                    s.type = 'h'
                                elif os.path.exists(file):
                                    mime = \
                                        mimetypes.guess_type(file)[0]
                                    if mime is None:  # is directory or binary
                                        if os.path.isdir(file):
                                            s.type = '1'
                                        else:
                                            s.type = '9'
                                            if file.endswith('.md'):
                                                s.type = 1
                                    else:
                                        for sw in mime_starts_with.keys():
                                            if mime.startswith(sw):
                                                s.type = \
                                                    mime_starts_with[
                                                        sw]
                            splt = file.split('/')
                            while '' in splt:
                                splt.remove('')
                            s.text = splt[len(splt) - 1]
                            if os.path.exists(file + '/gophertag'):
                                s.text = ''.join(list(open(
                                    file + '/gophertag'))).replace(
                                    '\r\n', '').replace('\n', '')
                            s.path = file.replace(pub_dir, '/', 1)
                            s.path = re.sub(r'/{2}', r'/', s.path)
                            s.host = host
                            s.port = port
                            if s.type == 'i':
                                s.path = ''
                                s.host = ''
                                s.port = '0'
                            if s.type == '1':
                                d = 0
                            else:
                                d = 1
                            if not s.path.endswith('gophermap'):
                                if not s.path.endswith(
                                        'gophertag'):
                                    listing.append(
                                        [file, s, s.text, d])

                        listing = natsorted(listing,
                                            key=itemgetter(0))
                        listing = natsorted(listing,
                                            key=itemgetter(2))
                        listing = natsorted(listing,
                                            key=itemgetter(3))

                        for item in listing:
                            new_menu.append(item[1])
                    else:
                        new_menu.append(errors['403_glob'])

            if not expanded:
                item = Item()
                item.type = itype
                item.text = text
                item.path = path
                item.host = host
                item.port = port

                if item.type == '?':
                    item.type = '9'
                    if path.startswith('URL:'):
                        item.type = 'h'
                    elif os.path.exists(
                            pub_dir + path):
                        mime = mimetypes.guess_type(
                            pub_dir + path)[0]
                        if mime is None:  # is directory or binary
                            if os.path.isdir(file):
                                s.type = '1'
                            else:
                                s.type = '9'
                        else:
                            for sw in mime_starts_with.keys():
                                if mime.startswith(sw):
                                    item.type = \
                                        mime_starts_with[sw]

                if item.host == def_host and item.port == def_port:
                    item.tls = tls

                new_menu.append(item.source())
        else:
            item = 'i' + item + '\t\t\t0'
            new_menu.append(item)
    return new_menu


def handle(request):
    """
    *Server.* Default handler function for Gopher requests while hosting a server.
    Serves files and directories from the pub/ directory by default, but the path can
    be changed in serve's pub_dir argument or changing the Request's pub_dir directory.
    """
    #####
    pub_dir = request.pub_dir
    #####

    if request.advertised_port is None:
        request.advertised_port = request.port
    if request.path.startswith('URL:'):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gopher Redirect</title>
            <meta http-equiv="refresh" content="0; url={0}">
        </head>
        <body>
            <h1>Gopher Redirect</h1>
            <p>You will be redirected to <a href="{0}">{0}</a> shortly.</p>
        </body>
        """.format(request.path.split('URL:')[1])

    if not os.path.exists(pub_dir):
        return [errors['no_pub_dir']]

    menu = []
    if request.path == '':
        request.path = '/'
    res_path = os.path.abspath(
        (pub_dir + request.path).replace('\\', '/').replace('//', '/'))
    if not res_path.startswith(os.path.abspath(pub_dir)):
        # Reject connections that try to break out of the publish directory
        return [errors['403']]
    if os.path.isdir(res_path):
        # is directory
        if os.path.exists(res_path):
            if os.path.isfile(res_path + '/gophermap'):
                in_file = open(res_path + '/gophermap', "r+")
                gmap = in_file.read()
                in_file.close()
                menu = parse_gophermap(source=gmap,
                                       def_host=request.host,
                                       def_port=request.advertised_port,
                                       gophermap_dir=request.path,
                                       pub_dir=pub_dir,
                                       tls=request.tls)
            else:
                gmap = '?*\t\r\n'
                menu = parse_gophermap(source=gmap,
                                       def_host=request.host,
                                       def_port=request.advertised_port,
                                       gophermap_dir=request.path,
                                       pub_dir=pub_dir,
                                       tls=request.tls)
            return menu
    elif os.path.isfile(res_path):
        mime_type, _ = mimetypes.guess_type(res_path)
        if mime_type == 'application/pdf':
            with open(res_path, "rb") as in_file:
                data = in_file.read()
            return data
        
        in_file = open(res_path, "rb")
        data = in_file.read()
        in_file.close()
        return data

    if request.alt_handler:
        alt = request.alt_handler(request)
        if alt:
            return alt

    e = errors['404']
    e.text = e.text.format(request.path)
    return [e]


def serve(host="127.0.0.1", port=70, advertised_port=None,
          handler=handle, pub_dir='pub/', alt_handler=False,
          send_period=False, tls=False, run_http=False, http_port=8080,
          tls_cert_chain='cacert.pem',
          tls_private_key='privkey.pem', debug=True):
    """
    *Server.*  Starts serving Gopher requests. Allows for using a custom handler that will return a Bytes, String, or List
    object (which can contain either Strings or Items) to send to the client, or the default handler which can serve
    a directory. Along with the default handler, you can set an alternate handler to use if a 404 error is generated for
    dynamic applications.
    """
    if pub_dir is None or pub_dir == '':
        pub_dir = '.'
    if tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        if os.path.exists(tls_cert_chain) and os.path.exists(tls_private_key):
            context.load_cert_chain(tls_cert_chain, tls_private_key)
        else:
            print("""TLS certificate and/or private key is missing. TLS has been disabled for this session.
Run this command to generate a self-signed certificate and private key:
    openssl req -x509 -newkey rsa:4096 -keyout {} -out {} -days 365
Note that clients may refuse to connect to a self-signed certificate.
            """.format(tls_private_key, tls_cert_chain))
            tls = False

    if tls:
        print('S/Gopher server is now running on',
              host + ':' + str(port) + '.')
    else:
        print('Gopher server is now running on', host + ':' + str(port) + '.')

    class GopherProtocol(asyncio.Protocol):
        def connection_made(self, transport):
            self.transport = transport
            print('Connected by', transport.get_extra_info('peername'))

        def data_received(self, data):
            request = data.decode('utf-8').replace('\r\n', '').split('\t')
            path = request[0]
            query = ''
            if len(request) > 1:
                query = request[1]
            if debug:
                print('Client requests: {}'.format(request))
            is_tls = False

            if self.transport.get_extra_info('sslcontext'):
                is_tls = True

            resp = handler(
                Request(path=path, query=query, host=host,
                        port=port, advertised_port=advertised_port,
                        client=self.transport.get_extra_info(
                            'peername')[0], pub_dir=pub_dir,
                        alt_handler=alt_handler, tls=is_tls))

            if type(resp) == str:
                resp = bytes(resp, 'utf-8')
            elif type(resp) == list:
                out = ""
                for line in resp:
                    if type(line) == Item:
                        out += line.source()
                    elif type(line) == str:
                        line = line.replace('\r\n', '\n')
                        line = line.replace('\n', '\r\n')
                        if not line.endswith('\r\n'):
                            line += '\r\n'
                        out += line
                resp = bytes(out, 'utf-8')
            elif type(resp) == Item:
                resp = bytes(resp.source(), 'utf-8')

            self.transport.write(resp)
            if send_period:
                self.transport.write(b'.')

            self.transport.close()
            if debug:
                print('Connection closed')

    class HTTPHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            if path == '/':
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><head><title>Gopher over HTTP</title></head>")
                self.wfile.write(b"<body><h1>Welcome to the Gopher over HTTP server</h1>")
                self.wfile.write(b'<ul><li><a href="/pub/">Browse Gopher pub directory</a></li></ul>')
                self.wfile.write(b"</body></html>")
                return

            if path.startswith('/pub/'):
                relative_path = path[len('/pub/'):]
            else:
                relative_path = path.lstrip('/')

            response, mime_type = self.handle_http_gopher_request(relative_path)

            if isinstance(response, bytes):
                self.send_response(200)
                self.send_header("Content-type", mime_type)
                self.end_headers()
                self.wfile.write(response)
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body>")
                self.wfile.write(response.encode())
                self.wfile.write(b"</body></html>")

        def handle_http_gopher_request(self, path):
            file_path = os.path.join(pub_dir, path)

            # Check if directory contains a gophermap and use it if present
            if os.path.isdir(file_path):
                gophermap_path = os.path.join(file_path, 'gophermap')
                if os.path.isfile(gophermap_path):
                    # Parse gophermap as Gopher menu
                    response = "<h2>Gopher HTTP Menu</h2><div>"
                    with open(gophermap_path, 'r') as f:
                        for line in f:
                            line = line.rstrip('\n')
                            if line:
                                item_type = line[0]
                                parts = line[1:].split('\t')
                                label = parts[0]
                                item_path = parts[1] if len(parts) > 1 else ''
                                icon = icons[item_type] if item_type in icons else icons['default']
                                # Map Gopher item types to HTML format
                                if item_type == '1':  # Directory
                                    item_path = item_path.strip('/')
                                    response += f'<div><img src="{icon}" alt="dir"> <a href="/pub/{item_path}">{label}/</a></div>'
                                elif item_type == '0':  # Text file
                                    item_path = item_path.strip('/')
                                    response += f'<div><img src="{icon}" alt="txt"> <a href="/pub/{item_path}">{label}</a></div>'
                                elif item_type == 'i':  # Informational text
                                    response += f'<div><img src="{icon}" alt="info"> <pre>{label}</pre></div>'
                                elif item_type in ('h', 'P', 'I', '7', 's', 'g'):
                                    item_path = item_path.strip('/')
                                    response += f'<div><img src="{icon}" alt="link"> <a href="/{item_path}">{label}</a></div>'
                                else:  # Fallback for unknown types
                                    response += f'<div><pre>{label}</pre></div>'
                    response += "</div>"
                    return response, "text/html"
                else:
                    # No gophermap, fallback to directory listing
                    entries = os.listdir(file_path)
                    response = f"<h2>Directory listing for /pub/{path}</h2><div>"
                    for entry in entries:
                        entry_path = os.path.join(path, entry)
                        icon = icons['1']
                        if os.path.isdir(os.path.join(pub_dir, entry_path)):
                            response += f'<div><img src="{icon}" alt="dir"> <a href="/pub/{entry_path}/">{entry}/</a></div>'
                        else:
                            response += f'<div><img src="{icon}" alt="file"> <a href="/pub/{entry_path}">{entry}</a></div>'
                    response += "</div>"
                    return response, "text/html"

            elif os.path.isfile(file_path):
                mime_type, _ = mimetypes.guess_type(file_path)
                with open(file_path, 'rb') as f:
                    return f.read(), mime_type or 'application/octet-stream'

            return "<h2>Error: Resource not found</h2>", "text/html"
 
    def run_http_server():
        httpd = http.server.HTTPServer(('localhost', http_port), HTTPHandler)
        print(f"HTTP wrapper running on http://localhost:{http_port}")
        httpd.serve_forever()

    async def main(h, p):
        loop = asyncio.get_running_loop()
        if tls:
            server = await loop.create_server(GopherProtocol, h, p, ssl=context)
        else:
            server = await loop.create_server(GopherProtocol, h, p)
        
        if run_http:
            http_thread = Thread(target=run_http_server)
            http_thread.start()
            print("HTTP server running in a separate thread.")
        
        await server.serve_forever()

    asyncio.run(main('0.0.0.0', port))