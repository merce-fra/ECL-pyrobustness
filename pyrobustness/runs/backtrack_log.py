# coding=utf-8
from __future__ import annotations

from dataclasses import dataclass, asdict

from enum import IntEnum
from fractions import Fraction
from typing import NamedTuple, List, Dict, Any, Optional, Union

from pyrobustness.ta.timedauto import Configuration
from pyrobustness.ta.interval import Interval
from pyrobustness.dtype import Delay


class DebugPart(IntEnum):
    START_INTERVAL = 1
    END_INTERVAL = 2
    END_ALL_INTERVALS = 3
    START_DELAY = 4
    END_DELAY = 5
    END_ALL_DELAYS = 6
    START_CONFIG = 7
    CYCLE_EXCEPTION = 8
    BOUND_EXCEPTION = 9
    FILTERED_OUT_INTERVAL = 10
    GOAL_REACHED = 11


@dataclass
class LogPart( object ) :
    formatting_str: str
    inner_data: List[ LogPart ]
    bonus_indent: int
    other: Dict[ str, str ]

    def get_str( self, indent: int = 0 ) -> str :
        tabs = "\t" * indent
        inner_str: str = "\n".join(
            [ d.get_str( indent + self.bonus_indent ) for d in self.inner_data ] )

        return self.formatting_str.format(
            **asdict( self ),
            **self.other,
            tabs=tabs,
            inner_str=inner_str
        )


@dataclass
class IntervalLog( LogPart ) :
    interval: Interval
    action: str
    perm: Optional[ Delay ]


@dataclass
class DelayLog( LogPart ) :
    delay: Delay
    perm: Optional[ Delay ]


@dataclass
class ConfigLog( LogPart ) :
    location: int
    valuation: List[ Union[ int, Fraction ] ]
    perm: Delay


@dataclass
class EndAllIntervalLog( LogPart ) :
    acc_max: List[ Delay ]
    perm: Delay


@dataclass
class EndAllDelayLog( LogPart ) :
    acc_min: List[ Delay ]
    perm: Delay


@dataclass
class FilteredOutIntervalLog( LogPart ) :
    pass


@dataclass
class ReachedGoalLog( LogPart ) :
    pass


@dataclass
class CycleExceptionLog( LogPart ) :
    e: Exception


@dataclass
class TraceExceptionLog( LogPart ) :
    e: Exception


class BaseLogger( object ) :
    def __init__( self, file=None ) :
        self.data: List[ LogPart ] = [ ]
        self.file: Optional[ str ] = file
        self.current_data: List[ int ] = [ ]

    def __call__( self, part: DebugPart, trace, *args, **kwargs ) :
        if part == DebugPart.START_INTERVAL :
            self.start_interval( **kwargs )
        elif part == DebugPart.END_INTERVAL :
            self.end_interval( **kwargs )
        elif part == DebugPart.END_ALL_INTERVALS :
            self.end_all_intervals( **kwargs )
        elif part == DebugPart.START_DELAY :
            self.start_delay( **kwargs )
        elif part == DebugPart.END_DELAY :
            self.end_delay( **kwargs )
        elif part == DebugPart.END_ALL_DELAYS :
            self.end_all_delays( **kwargs )
        elif part == DebugPart.START_CONFIG :
            self.start_config( **kwargs )
        elif part == DebugPart.CYCLE_EXCEPTION :
            self.cycle_exception( **kwargs )
        elif part == DebugPart.BOUND_EXCEPTION :
            self.cycle_exception( **kwargs )
        elif part == DebugPart.FILTERED_OUT_INTERVAL :
            self.filtered_out_interval()
        elif part == DebugPart.GOAL_REACHED :
            self.goal_reached()

        return

    def get_current_sub_data( self ) :
        if len( self.current_data ) == 0 :
            return None

        data = self.data[ self.current_data[ 0 ] ]
        for i in self.current_data[ 1 : ] :
            data = data.inner_data[ i ]

        return data

    def start_config( self, config, perm ) :
        pass

    def start_interval( self, action, interval ) :
        pass

    def start_delay( self, delay ) :
        pass

    def end_delay( self, perm ) :
        pass

    def end_all_delays( self, acc_min, perm ) :
        pass

    def end_interval( self, perm ) :
        pass

    def filtered_out_interval( self ) :
        pass

    def end_all_intervals( self, acc_max, perm ) :
        pass

    def goal_reached( self ) :
        pass

    def cycle_exception( self, e ) :
        pass

    def trace_exception( self, e ) :
        pass

    def emit( self ) :
        if self.file is None :
            print( "\n".join( map( lambda d : d.get_str(), self.data ) ) )
        else :
            with open( self.file, "w" ) as f :
                f.write( "\n".join( map( lambda d : d.get_str(), self.data ) ) )


class BacktrackConsoleLoggerBis( BaseLogger ) :
    def start_config( self, config, perm ) :
        log = ConfigLog(
            formatting_str="{tabs}C> {location}  {valuation}  |  {perm}\n{inner_str}",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            location=config.location,
            valuation=config.valuation,
            perm=perm )

        if len( self.current_data ) == 0 :
            # No data to place the data into
            self.current_data.append( len( self.data ) )
            self.data.append( log )
        else :
            data = self.get_current_sub_data()
            if type( data ) != DelayLog :
                raise Exception( "Starting config while not in an DelayLog" )
            self.current_data.append( len( data.inner_data ) )
            data.inner_data.append( log )

    def start_interval( self, action, interval ) :
        log = IntervalLog(
            formatting_str="{tabs}I> \"{action}\" : {interval}  |  {perm}\n{inner_str}",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            action=action,
            interval=interval,
            perm=None )

        data = self.get_current_sub_data()
        if type( data ) != ConfigLog :
            raise Exception( "Starting interval while not in an ConfigLog" )
        self.current_data.append( len( data.inner_data ) )
        data.inner_data.append( log )

    def start_delay( self, delay ) :
        log = DelayLog(
            formatting_str="{tabs}d> {delay}  |  {perm}\n{inner_str}",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            delay=delay,
            perm=None )

        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Starting delay while not in an IntervalLog" )
        self.current_data.append( len( data.inner_data ) )
        data.inner_data.append( log )

    def end_delay( self, perm ) :
        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "Ending delay of a non DelayLog" )
        data.perm = perm
        self.current_data.pop()

    def end_all_delays( self, acc_min, perm ) :
        log = EndAllDelayLog(
            formatting_str="{tabs}m> min({acc_min}) = {perm}",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            acc_min=acc_min,
            perm=perm )

        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Ending all delay in a non IntervalLog" )
        data.inner_data.append( log )

    def end_interval( self, perm ) :
        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Ending interval of a non IntervalLog" )
        data.perm = perm
        self.current_data.pop()

    def filtered_out_interval( self ) :
        log = FilteredOutIntervalLog(
            formatting_str="{tabs}Filtered out",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
        )

        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Filtering out a non IntervalLog" )
        data.perm = None
        data.inner_data.append( log )
        self.current_data.pop()

    def end_all_intervals( self, acc_max, perm ) :
        log = EndAllIntervalLog(
            formatting_str="{tabs}M> max({acc_max}) = {perm}",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            acc_max=acc_max,
            perm=perm
        )

        data = self.get_current_sub_data()
        if type( data ) != ConfigLog :
            raise Exception( "End all intervals without begin in a ConfigLog" )
        data.inner_data.append( log )
        self.current_data.pop()

    def goal_reached( self ) :
        log = ReachedGoalLog(
            formatting_str="{tabs}Backtrack reached GOAL",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
        )

        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "Goal is not inside a delay" )
        data.perm = None
        data.inner_data.append( log )

    def cycle_exception( self, e ) :
        log = CycleExceptionLog(
            formatting_str="{tabs}E> Backtrack interrupted because cycle bound as been reached",
            inner_data=[],
            bonus_indent=1,
            other={},
            e=e
        )

        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "CycleBoundException is not inside a delay" )
        data.perm = None
        data.inner_data.append( log )
        self.current_data.pop()

    def trace_exception( self, e ) :
        log = CycleExceptionLog(
            formatting_str="{tabs}E> Backtrack interrupted because trace bound as been reached",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            e=e
        )

        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "TraceBoundException is not inside a delay" )
        data.perm = None
        data.inner_data.append( log )
        self.current_data.pop()

class BacktrackHTMLLoggerBis( BaseLogger ):
    @dataclass
    class HTMLFrameLog( LogPart ):
        js: str
        css: str

    def __init__( self, file=None ) :
        super().__init__(file)

        formatting_str = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Backtrack Logger</title>
    </head>
    <body>
    <button class="button-filtered-out-interval">
        Hide filtered out
    </button>

    {inner_str}
    </body>

    {css}
    {js}
    </html>"""

        log = BacktrackHTMLLoggerBis.HTMLFrameLog(
            formatting_str=formatting_str,
            inner_data=[ ],
            bonus_indent=2,
            other={ },
            js=self.emit_js(),
            css=self.emit_css()
        )

        self.current_data.append( len(self.data) )
        self.data.append( log )

    def start_config( self, config, perm ) :
        formatting_str = """{tabs}<div class="div-config">
{tabs}    <table class="table-config">
{tabs}        <tbody>
{tabs}            <tr>
{tabs}                <td class="td-config-data" title="location">{location}</td>
{tabs}                <td class="td-config-data" title="valuation">{valuation}</td>
{tabs}                <td class="td-config-data" title="trace permissiveness">{perm}</td>
{tabs}            </tr>
{tabs}        </tbody>
{tabs}    </table>
{inner_str}
{tabs}</div>"""

        log = ConfigLog(
            formatting_str=formatting_str,
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            location=config.location,
            valuation=config.valuation,
            perm=perm )

        if len( self.current_data ) == 0 :
            # No data to place the data into
            self.current_data.append( len( self.data ) )
            self.data.append( log )
        else :
            data = self.get_current_sub_data()
            if type( data ) != DelayLog and type( data ) != BacktrackHTMLLoggerBis.HTMLFrameLog :
                raise Exception( "Starting config while not in an DelayLog" )
            self.current_data.append( len( data.inner_data ) )
            data.inner_data.append( log )

    def start_interval( self, action, interval ) :
        formatting_str = """{tabs}<button class="accordion-interval{class_ext}">
{tabs}    <table class="table-interval">
{tabs}        <tbody>
{tabs}            <tr>
{tabs}                <td class="td-interval">"{action}" : {interval}</td>
{tabs}                <td class="td-interval-permissiveness">{perm}</td>
{tabs}            </tr>
{tabs}        </tbody>
{tabs}    </table>
{tabs}</button>
{tabs}<div class="panel-interval{class_ext}">
{inner_str}
{tabs}</div>"""
        log = IntervalLog(
            formatting_str=formatting_str,
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            action=action,
            interval=interval,
            perm=None )

        data = self.get_current_sub_data()
        if type( data ) != ConfigLog :
            raise Exception( "Starting interval while not in an ConfigLog" )
        self.current_data.append( len( data.inner_data ) )
        data.inner_data.append( log )

    def start_delay( self, delay ) :
        formatting_str = """{tabs}<button class="accordion-delay">
{tabs}    <table class="table-delay">
{tabs}        <tbody>
{tabs}            <tr>
{tabs}                <td class="td-delay">{delay}</td>
{tabs}                <td class="td-delay-permissiveness">{perm}</td>
{tabs}            </tr>
{tabs}        </tbody>
{tabs}    </table>
{tabs}</button>
{tabs}<div class="panel-delay">
{inner_str}
{tabs}</div>"""

        log = DelayLog(
            formatting_str=formatting_str,
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            delay=delay,
            perm=None )

        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Starting delay while not in an IntervalLog" )
        self.current_data.append( len( data.inner_data ) )
        data.inner_data.append( log )

    def end_delay( self, perm ) :
        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "Ending delay of a non DelayLog" )
        data.perm = perm
        self.current_data.pop()

    def end_all_delays( self, acc_min, perm ) :
        formatting_str = "{tabs}<div class=\"div-min\">min delay = {perm}</div>"
        log = EndAllDelayLog(
            formatting_str=formatting_str,
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            acc_min=acc_min,
            perm=perm )

        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Ending all delay in a non IntervalLog" )
        data.inner_data.append( log )

    def end_interval( self, perm ) :
        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Ending interval of a non IntervalLog" )
        data.perm = perm
        data.other["class_ext"] = ""
        self.current_data.pop()

    def filtered_out_interval( self ) :
        log = FilteredOutIntervalLog(
            formatting_str="{tabs}<p>Filtered out</p>",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
        )

        data = self.get_current_sub_data()
        if type( data ) != IntervalLog :
            raise Exception( "Filtering out a non IntervalLog" )
        data.perm = None
        data.other["class_ext"] = "-filtered-out"
        data.inner_data.append( log )
        self.current_data.pop()

    def end_all_intervals( self, acc_max, perm ) :
        formatting_str = "{tabs}<div class=\"div-max\">max interval = {perm}</div>"
        log = EndAllIntervalLog(
            formatting_str=formatting_str,
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            acc_max=acc_max,
            perm=perm
        )

        data = self.get_current_sub_data()
        if type( data ) != ConfigLog :
            raise Exception( "End all intervals without begin in a ConfigLog" )
        data.inner_data.append( log )
        self.current_data.pop()

    def goal_reached( self ) :
        log = ReachedGoalLog(
            formatting_str="{tabs}<p>Goal reached</p>",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
        )

        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "Goal is not inside a delay" )
        data.perm = None
        data.inner_data.append( log )

    def cycle_exception( self, e ) :
        log = CycleExceptionLog(
            formatting_str="{tabs}<p>Cycle bound reached<p>",
            inner_data=[],
            bonus_indent=1,
            other={},
            e=e
        )

        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "CycleBoundException is not inside a delay" )
        data.perm = None
        data.inner_data.append( log )
        self.current_data.pop()

    def trace_exception( self, e ) :
        log = CycleExceptionLog(
            formatting_str="{tabs}<p>Cycle bound reached<p>",
            inner_data=[ ],
            bonus_indent=1,
            other={ },
            e=e
        )

        data = self.get_current_sub_data()
        if type( data ) != DelayLog :
            raise Exception( "TraceBoundException is not inside a delay" )
        data.perm = None
        data.inner_data.append( log )
        self.current_data.pop()

    def emit_js( self ) :
        data = """<script>
        var acc_interval = document.getElementsByClassName("accordion-interval");
        var acc_interval_filtered_out = document.getElementsByClassName("accordion-interval-filtered-out");
        var acc_delay = document.getElementsByClassName("accordion-delay");
        var i;

        for (i = 0; i < acc_interval.length; i++) {
            acc_interval[i].addEventListener("click", function() {
                /* Toggle between adding and removing the "active" class,
                to highlight the button that controls the panel */
                this.classList.toggle("active-interval");

                /* Toggle between hiding and showing the active panel */
                var panel = this.nextElementSibling;
                if (panel.style.display === "block") {
                  panel.style.display = "none";
                } else {
                  panel.style.display = "block";
                }
            });
        }

        for (i = 0; i < acc_delay.length; i++) {
            acc_delay[i].addEventListener("click", function() {
                /* Toggle between adding and removing the "active" class,
                to highlight the button that controls the panel */
                this.classList.toggle("active-delay");

                /* Toggle between hiding and showing the active panel */
                var panel = this.nextElementSibling;
                if (panel.style.display === "block") {
                  panel.style.display = "none";
                } else {
                  panel.style.display = "block";
                }
            });
        }

        for (i = 0; i < acc_interval_filtered_out.length; i++) {
            acc_interval_filtered_out[i].addEventListener("click", function() {
                /* Toggle between adding and removing the "active" class,
                to highlight the button that controls the panel */
                this.classList.toggle("active-interval-filtered-out");

                /* Toggle between hiding and showing the active panel */
                var panel = this.nextElementSibling;
                if (panel.style.display === "block") {
                  panel.style.display = "none";
                } else {
                  panel.style.display = "block";
                }
            });
        }

        button_hide_filtered_out = document.getElementsByClassName("button-filtered-out-interval");
        for (i = 0; i < button_hide_filtered_out.length; i++) {
            button_hide_filtered_out[i].addEventListener("click", function() {
                /* Toggle between adding and removing the "active" class,
                to highlight the button that controls the panel */
                // this.classList.toggle("active-button-filtered-out-interval");

                for (k = 0; k < acc_interval_filtered_out.length; k++) {
                    if (acc_interval_filtered_out[k].style.display == "block") {
                        var panel = acc_interval_filtered_out[k].nextElementSibling;
                        acc_interval_filtered_out[k].style.display = "none";
                        panel.style.display = "none";
                    } else {
                        acc_interval_filtered_out[k].style.display = "block";
                    }
                }
            });
        }
    </script>"""

        return data

    def emit_css( self ) :
        data = """<style>
        /* Style the accordion */

        .accordion-interval, .accordion-delay, .accordion-interval-filtered-out {
            cursor: pointer;
            padding: 14px;
            width: 100%;
            text-align: left;
            border: 1px solid;
            outline: none;
            transition: 0.4s;
            border-collapse: collapse;
        }

        .accordion-interval-filtered-out {
            background-color: #d6dbdf;
            color: #444;
        }

        .accordion-interval {
            background-color: #fad7a0;
            color: #444;
        }

        .accordion-delay {
            background-color: #a3e4d7;
            color: #444;
        }

        .active-interval, .accordion-interval:hover {
            background-color: #f5b041;
        }

        .active-interval-filtered-out, .accordion-interval-filtered-out:hover {
            background-color: #d6dbdf;
        }

        .active-delay, .accordion-delay:hover {
            background-color: #1abc9c;
        }

        /* Style for the panel inside accordions */

        .panel-interval, .panel-delay, .panel-interval-filtered-out {
            padding: 0 4px;
            border-left: 1px solid;
            border-bottom: 1px solid;
            display: none;
            overflow: hidden;
            border-collapse: collapse;
        }

        .panel-interval {
            background-color: #f7dc6f;
        }

        .panel-interval-filtered-out {
            background-color: #d6dbdf;
        }

        .panel-delay {
            background-color: #58d68d;
        }

        /* Style of the tables */

        .table-config, .table-interval, .table-delay {
            text-align: left;
            width: 100%;
            border-collapse: collapse;
        }

        .table-config {
            border: 1px solid;
            background-color: #f5b7b1;
        }

        .table-interval {
            border: none;
        }

        /* Style of cells for interval and delay */
        .td-interval, .td-delay {
            border-right: 1px solid;
            text-align: left;
            width: 25%;
            border-collapse: collapse;
        }

        .td-interval-permissiveness, .td-delay-permissiveness {
            border-right: none;
            text-align: left;
            width: 75%;
            padding-left: 4px;
            border-collapse: collapse;
        }

        /* Style for the config cells */
        .td-config-data {
            border-width: 1px;
            border-style: solid;
            text-align: center;
            width: 33%;
            border-collapse: collapse;
            padding: 4px 6px;
         }

        /* Style for the min-max */
        .div-min, .div-max {
            padding: 4px;
        }

        .button-filtered-out-interval {
            background: red;
            cursor: pointer;
            padding: 4px;
            text-align: center;
            border: 1px solid;
            outline: none;
        }
    </style>"""

        return data

class BacktrackConsoleLogger( object ) :
    def __init__( self, file=None ) :
        self.data = [ ]
        self.file = file

    def __call__( self, part: DebugPart, *args, **kwargs ) :
        if part == DebugPart.START_INTERVAL :
            self.start_interval( **kwargs )
        elif part == DebugPart.END_INTERVAL :
            self.end_interval( **kwargs )
        elif part == DebugPart.END_ALL_INTERVALS :
            self.end_all_intervals( **kwargs )
        elif part == DebugPart.START_DELAY :
            self.start_delay( **kwargs )
        elif part == DebugPart.END_DELAY :
            self.end_delay( **kwargs )
        elif part == DebugPart.END_ALL_DELAYS :
            self.end_all_delays( **kwargs )
        elif part == DebugPart.START_CONFIG :
            self.start_config( **kwargs )
        elif part == DebugPart.GENERAL_EXCEPTION :
            self.general_exception( **kwargs )
        elif part == DebugPart.CYCLE_EXCEPTION :
            self.cycle_exception( **kwargs )
        elif part == DebugPart.BOUND_EXCEPTION :
            self.cycle_exception( **kwargs )
        elif part == DebugPart.FILTERED_OUT_INTERVAL :
            self.filtered_out_interval( **kwargs )
        elif part == DebugPart.GOAL_REACHED :
            self.goal_reached( **kwargs )

    def start_config( self, config, trace, perm ) :
        tabs = "\t" * (2 * len( trace ))
        self.data.append( tabs + "-> " + str( config ) + " : " + str( perm ) )

    def start_interval( self, trace, action, interval ) :
        tabs = "\t" * (2 * len( trace ))
        self.data.append( tabs + "-> \"" + str( action ) + "\" : " + str( interval ) )

    def start_delay( self, trace, delay ) :
        tabs = "\t" * (2 * len( trace ) + 1)
        self.data.append( tabs + "-> " + str( delay ) )

    def end_delay( self, trace, perm ) :
        tabs = "\t" * (2 * len( trace ) + 1)
        self.data.append( tabs + "perm delay = " + str( perm ) )

    def end_all_delays( self, trace, acc_min, perm ) :
        tabs = "\t" * (2 * len( trace ) + 1)
        self.data.append( tabs + "   min(" + str( acc_min ) + ") = " + str( perm ) )

    def end_interval( self, trace, perm ) :
        tabs = "\t" * (2 * len( trace ))
        self.data.append( tabs + "perm interval = " + str( perm ) )

    def filtered_out_interval( self, trace ) :
        tabs = "\t" * (2 * len( trace ))
        self.data.append( tabs + "Filtered out" )

    def end_all_intervals( self, trace, acc_max, perm ) :
        tabs = "\t" * (2 * len( trace ))
        self.data.append( tabs + "   max(" + str( acc_max ) + ") = " + str( perm ) )

    def goal_reached( self, trace ) :
        tabs = "\t" * (2 * len( trace ) + 1)
        self.data.append( tabs + "Backtrack reached GOAL" )

    def general_exception( self, trace, e ) :
        self.data.append( "Exception : " + str( e ) )

    def cycle_exception( self, trace, e ) :
        self.data.append( "Backtrack interrupted because cycle bound has been reached" )

    def trace_exception( self, trace, e ) :
        self.data.append( "Backtrack interrupted because trace bound has been reached" )

    def emit( self ) :
        if self.file is None :
            print( "\n".join( self.data ) )
        else :
            with open( self.file, "w" ) as f :
                f.write( "\n".join( self.data ) )

class BacktrackHTMLLogger( object ) :
    def __init__( self, file ) :
        self.trace_missing_permissiveness = [ ]
        self.file = file
        self.data = [ ]

    def __call__( self, part: DebugPart, *args, **kwargs ) :
        if part == DebugPart.START_INTERVAL :
            self.start_interval( **kwargs )
        elif part == DebugPart.END_INTERVAL :
            self.end_interval( **kwargs )
        elif part == DebugPart.END_ALL_INTERVALS :
            self.end_all_intervals( **kwargs )
        elif part == DebugPart.START_DELAY :
            self.start_delay( **kwargs )
        elif part == DebugPart.END_DELAY :
            self.end_delay( **kwargs )
        elif part == DebugPart.END_ALL_DELAYS :
            self.end_all_delays( **kwargs )
        elif part == DebugPart.START_CONFIG :
            self.start_config( **kwargs )
        # elif part == DebugPart.GENERAL_EXCEPTION :
        #     self.general_exception( **kwargs )
        elif part == DebugPart.CYCLE_EXCEPTION :
            self.cycle_exception( **kwargs )
        elif part == DebugPart.BOUND_EXCEPTION :
            self.cycle_exception( **kwargs )
        elif part == DebugPart.FILTERED_OUT_INTERVAL :
            self.filtered_out_interval( **kwargs )
        elif part == DebugPart.GOAL_REACHED :
            self.goal_reached( **kwargs )

        return

    def start_config( self, config, trace, perm ) :
        tabs = "\t" * (3 * len( trace ))
        s = """{tabs}<div class="div-config">
{tabs}    <table class="table-config">
{tabs}        <tbody>
{tabs}            <tr>
{tabs}                <td class="td-config-data" title="location">{location}</td>
{tabs}                <td class="td-config-data" title="valuation">{valuation}</td>
{tabs}                <td class="td-config-data" title="trace permissiveness">{perm}</td>
{tabs}            </tr>
{tabs}        </tbody>
{tabs}    </table>""".format( location=str( config.location ), valuation=str( config.valuation ), perm=str( perm ),
                              tabs=tabs )
        self.data.append( s )

    def start_interval( self, trace, action, interval ) :
        tabs = "\t" * (3 * len( trace ) + 1)
        s = """{tabs}<button class="accordion-interval{class_ext}">
{tabs}    <table class="table-interval">
{tabs}        <tbody>
{tabs}            <tr>
{tabs}                <td class="td-interval">"{action}" : {interval}</td>
{tabs}                <td class="td-interval-permissiveness">{perm}</td>
{tabs}            </tr>
{tabs}        </tbody>
{tabs}    </table>
{tabs}</button>
{tabs}<div class="panel-interval{class_ext}">""".format(
            action=action,
            interval=interval,
            perm="{perm}",
            tabs=tabs,
            class_ext="{class_ext}"
        )
        self.data.append( s )
        self.trace_missing_permissiveness.append( len( self.data ) - 1 )

    def start_delay( self, trace, delay ) :
        tabs = "\t" * (3 * len( trace ) + 2)
        s = """{tabs}<button class="accordion-delay">
{tabs}    <table class="table-delay">
{tabs}        <tbody>
{tabs}            <tr>
{tabs}                <td class="td-delay">{delay}</td>
{tabs}                <td class="td-delay-permissiveness">{perm}</td>
{tabs}            </tr>
{tabs}        </tbody>
{tabs}    </table>
{tabs}</button>
{tabs}<div class="panel-delay">""".format(
            delay=delay,
            perm="{perm}",
            tabs=tabs
        )
        self.data.append(s)
        self.trace_missing_permissiveness.append(len(self.data) - 1)

    def end_delay( self, trace, perm ) :
        tabs = "\t" * (3 * len( trace ) + 2)
        s = "{tabs}</div>".format( tabs=tabs )
        self.data.append( s )
        prev_data = self.trace_missing_permissiveness.pop()
        self.data[ prev_data ] = self.data[ prev_data ].format( perm=perm )

    def end_all_delays( self, trace, acc_min, perm ) :
        tabs = "\t" * (3 * len( trace ) + 2)
        s = """{tabs}<div class="div-min">min delay = {perm}</div>""".format(
            perm=perm,
            tabs=tabs
        )
        self.data.append(s)

    def end_all_intervals( self, trace, acc_max, perm ) :
        tabs = "\t" * (3 * len( trace ))
        s = """{tabs}    <div class="div-max">max interval = {perm}</div>
{tabs}</div>""".format( perm=perm, tabs=tabs )
        self.data.append( s )

    def end_interval( self, trace, perm ) :
        tabs = "\t" * (3 * len( trace ) + 1)
        s = """{tabs}</div>""".format( tabs=tabs )
        self.data.append( s )
        prev_data = self.trace_missing_permissiveness.pop()
        self.data[prev_data] = self.data[prev_data].format(perm=perm, class_ext="")

    def filtered_out_interval( self, trace ) :
        tabs = "\t" * (3 * len( trace ) + 1)
        s = """{tabs}<p>Filtered out</p>
{tabs}</div>""".format( tabs=tabs )
        self.data.append( s )
        prev_data = self.trace_missing_permissiveness.pop()
        self.data[prev_data] = self.data[prev_data].format(perm=None, class_ext="-filtered-out")

    def goal_reached( self, trace ) :
        tabs = "\t" * (3 * len( trace ) + 1)
        s = """{tabs}<p>Goal reached</p>""".format( tabs=tabs )
        self.data.append( s )

    def general_exception(self, trace, e):
        s = """<p>Interrupted by the following exception : {e}<p>
</div>""".format( e=str( e ) )
        self.data.append( s )
        prev_data = self.trace_missing_permissiveness.pop()
        self.data[prev_data] = self.data[prev_data].format(perm=None)

    def cycle_exception( self, trace, e ) :
        tabs = "\t" * (3 * len( trace ) - 1)
        s = """{tabs}   <p>Cycle bound reached<p>
{tabs}</div>""".format( tabs=tabs )
        self.data.append( s )
        prev_data = self.trace_missing_permissiveness.pop()
        self.data[prev_data] = self.data[prev_data].format(perm=None)

    def trace_exception(self, trace, e):
        s = """<p>Trace bound reached<p>
</div>"""
        self.data.append(s)
        prev_data = self.trace_missing_permissiveness.pop()
        self.data[prev_data] = self.data[prev_data].format(perm=None)

    def emit_js( self ) :
        data = """<script>
    var acc_interval = document.getElementsByClassName("accordion-interval");
    var acc_interval_filtered_out = document.getElementsByClassName("accordion-interval-filtered-out");
    var acc_delay = document.getElementsByClassName("accordion-delay");
    var i;

    for (i = 0; i < acc_interval.length; i++) {
        acc_interval[i].addEventListener("click", function() {
            /* Toggle between adding and removing the "active" class,
            to highlight the button that controls the panel */
            this.classList.toggle("active-interval");

            /* Toggle between hiding and showing the active panel */
            var panel = this.nextElementSibling;
            if (panel.style.display === "block") {
              panel.style.display = "none";
            } else {
              panel.style.display = "block";
            }
        });
    }

    for (i = 0; i < acc_delay.length; i++) {
        acc_delay[i].addEventListener("click", function() {
            /* Toggle between adding and removing the "active" class,
            to highlight the button that controls the panel */
            this.classList.toggle("active-delay");

            /* Toggle between hiding and showing the active panel */
            var panel = this.nextElementSibling;
            if (panel.style.display === "block") {
              panel.style.display = "none";
            } else {
              panel.style.display = "block";
            }
        });
    }

    for (i = 0; i < acc_interval_filtered_out.length; i++) {
        acc_interval_filtered_out[i].addEventListener("click", function() {
            /* Toggle between adding and removing the "active" class,
            to highlight the button that controls the panel */
            this.classList.toggle("active-interval-filtered-out");

            /* Toggle between hiding and showing the active panel */
            var panel = this.nextElementSibling;
            if (panel.style.display === "block") {
              panel.style.display = "none";
            } else {
              panel.style.display = "block";
            }
        });
    }

    button_hide_filtered_out = document.getElementsByClassName("button-filtered-out-interval");
    for (i = 0; i < button_hide_filtered_out.length; i++) {
        button_hide_filtered_out[i].addEventListener("click", function() {
            /* Toggle between adding and removing the "active" class,
            to highlight the button that controls the panel */
            // this.classList.toggle("active-button-filtered-out-interval");

            for (k = 0; k < acc_interval_filtered_out.length; k++) {
                if (acc_interval_filtered_out[k].style.display == "block") {
                    var panel = acc_interval_filtered_out[k].nextElementSibling;
                    acc_interval_filtered_out[k].style.display = "none";
                    panel.style.display = "none";
                } else {
                    acc_interval_filtered_out[k].style.display = "block";
                }
            }
        });
    }
</script>"""

        return data

    def emit_css( self ) :
        data = """<style>
    /* Style the accordion */

    .accordion-interval, .accordion-delay, .accordion-interval-filtered-out {
        cursor: pointer;
        padding: 14px;
        width: 100%;
        text-align: left;
        border: 1px solid;
        outline: none;
        transition: 0.4s;
        border-collapse: collapse;
    }

    .accordion-interval-filtered-out {
        background-color: #d6dbdf;
        color: #444;
    }

    .accordion-interval {
        background-color: #fad7a0;
        color: #444;
    }

    .accordion-delay {
        background-color: #a3e4d7;
        color: #444;
    }

    .active-interval, .accordion-interval:hover {
        background-color: #f5b041;
    }

    .active-interval-filtered-out, .accordion-interval-filtered-out:hover {
        background-color: #d6dbdf;
    }

    .active-delay, .accordion-delay:hover {
        background-color: #1abc9c;
    }

    /* Style for the panel inside accordions */

    .panel-interval, .panel-delay, .panel-interval-filtered-out {
        padding: 0 4px;
        border-left: 1px solid;
        border-bottom: 1px solid;
        display: none;
        overflow: hidden;
        border-collapse: collapse;
    }

    .panel-interval {
        background-color: #f7dc6f;
    }

    .panel-interval-filtered-out {
        background-color: #d6dbdf;
    }

    .panel-delay {
        background-color: #58d68d;
    }

    /* Style of the tables */

    .table-config, .table-interval, .table-delay {
        text-align: left;
        width: 100%;
        border-collapse: collapse;
    }

    .table-config {
        border: 1px solid;
        background-color: #f5b7b1;
    }

    .table-interval {
        border: none;
    }

    /* Style of cells for interval and delay */
    .td-interval, .td-delay {
        border-right: 1px solid;
        text-align: left;
        width: 25%;
        border-collapse: collapse;
    }

    .td-interval-permissiveness, .td-delay-permissiveness {
        border-right: none;
        text-align: left;
        width: 75%;
        padding-left: 4px;
        border-collapse: collapse;
    }

    /* Style for the config cells */
    .td-config-data {
        border-width: 1px;
        border-style: solid;
        text-align: center;
        width: 33%;
        border-collapse: collapse;
        padding: 4px 6px;
     }

    /* Style for the min-max */
    .div-min, .div-max {
        padding: 4px;
    }

    .button-filtered-out-interval {
        background: red;
        cursor: pointer;
        padding: 4px;
        text-align: center;
        border: 1px solid;
        outline: none;
    }
</style>"""

        return data

    def emit( self ) :
        js = self.emit_js()
        css = self.emit_css()

        final_data = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Backtrack Logger</title>
</head>
<body>
<button class="button-filtered-out-interval">
    Hide filtered out
</button>

{data}
</body>

{css}
{js}
</html>""".format( data="\n".join( self.data ), js=js, css=css )

        with open( self.file, "w" ) as f :
            f.write( final_data )
