/* -*- mode: c; c-file-style: "bsd" -*-  */
/* $Id$ */
/* libhsync/trace.c -- Control debug trace, etc
   
   Copyright (C) 2000 by Martin Pool <mbp@humbug.org.au>

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
   USA */

#include "includes.h"
#include "hsync.h"
#include "private.h"

char const * const hs_libhsync_version = PACKAGE " " VERSION;

hs_trace_fn_t *_hs_trace_impl = hs_trace_to_stderr;


void
hs_trace_to(hs_trace_fn_t *new_impl)
{
     _hs_trace_impl = new_impl;
}


#ifdef DO_HS_TRACE
void
_hs_trace0(char const *fmt, ...)
{
     va_list va;
     
     if (_hs_trace_impl) {
	  va_start(va, fmt);
	  _hs_trace_impl(fmt, va);
	  va_end(va);
     }
}
#endif /* DO_HS_TRACE */


void
hs_trace_to_stderr(char const *fmt, va_list va)
{
    char buf[1000];
    int n;

    n = 0;
    buf[n++] = '\t';
    vsnprintf(buf+n, sizeof buf - 1, fmt, va);
    n = strlen(buf);
    buf[n++] = '\n';

    /* NOTE NO TRAILING NUL */
    write(STDERR_FILENO, buf, n);
}
