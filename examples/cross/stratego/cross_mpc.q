//This file was generated from (Academic) UPPAAL 4.1.20-stratego-8-beta6 (rev. 2B32AEEE2ECD4B4F), January 2021
/*

*/
strategy opt = minE (C) [<=HORIZON]{\
next_phase, phase, \
waiting[0], waiting[1], waiting[2], waiting[3],\
waiting[4], waiting[5], waiting[6], waiting[7],\
waiting[8], waiting[9], waiting[10], waiting[11],\
waiting[12], waiting[13], waiting[14], waiting[15],\
waiting[16], waiting[17], waiting[18], waiting[19]\
}->{t, ctrl.x}:<> t>=HORIZON


/*

*/
simulate 1 [<=HORIZON] {phase} under opt