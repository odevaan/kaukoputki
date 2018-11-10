function H=mod2pi(H);
%function H=mod2pi(H);
%
%Palauttaa luvut H välille 0<= H < 2*pi
%

pi2=6.28318530717959;
H=H-pi2*floor(H/pi2);