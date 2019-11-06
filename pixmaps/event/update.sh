#!/bin/bash

size="-w 64 -h 64"

inDir="../../svg/event"

inkscape --export-png alarm.png $size $inDir/alarm.svg
inkscape --export-png birthday.png $size $inDir/birthday.svg
inkscape --export-png birthday2.png $size $inDir/birthday2.svg
inkscape --export-png business.png $size $inDir/business.svg
inkscape --export-png education.png $size $inDir/education.svg
inkscape --export-png favorite.png $size $inDir/favorite.svg
inkscape --export-png green_clover.png $size $inDir/green_clover.svg
inkscape --export-png holiday.png $size $inDir/holiday.svg
inkscape --export-png important.png $size $inDir/important.svg
inkscape --export-png marriage.png $size $inDir/marriage.svg
inkscape --export-png note.png $size $inDir/note.svg
inkscape --export-png phone_call.png $size $inDir/phone_call.svg
inkscape --export-png task.png $size $inDir/task.svg
inkscape --export-png university.png $size $inDir/university.svg

