% ***********************************************
% An Introduction to Computational Macroeconomics
% A. Bongers, T. Gómez and J. L. Torres (2019)
% An example of a dynamic system in DYNARE
% Richardson's arms race model
% File: m1d.mod
%
% Transcribed verbatim from Appendix C of the book. Saddle-point
% calibration: numerical oracle for the saddle-path section of
% practica P0 (simulate_saddle_path in src/macroaicomp/models/arms_race.py).
% ***********************************************

// Endogenous variables
var x1 x2 dx1 dx2;

// Exogenous variables
varexo z1, z2;

// Parameters
parameters Alpha, Beta, Gamma, Delta, Theta, Ita;
Alpha = 0.25;
Beta = 0.5;
Gamma = 0.5;
Delta = 0.25;
Theta = 1.0;
Ita = 1.0;

// Model equations
model;
x1(+1) = x1+dx1;
x2 = x2(-1)+dx2(-1);
dx1 = -Alpha*x1+Beta*x2+Theta*z1;
dx2 = Gamma*x1-Delta*x2+Ita*z2;
end;

// Initial values
initval;
x1 = 4;
x2 = 4;
dx1 = 0;
dx2 = 0;
z1 = -1;
z2 = -1;
end;

// Calculation of the initial steady state
steady;
check;

// End values
endval;
x1 = 4;
x2 = 4;
dx1 = 0;
dx2 = 0;
z1 = -0.5;
z2 = -1;
end;

// Calculation of the final steady state
steady;

// Disturbance analysis
shocks;
var z1;
periods 0;
values 0;
end;

// Deterministic simulation
simul(periods=30);

// Graphics
T=30;
j=1:T;
figure;
subplot(1,2,1)
plot(j,x1(1:T),'Color',[0.5 0.5 0.5],'linewidth',2.5)
title('Armament stock country 1')
xlabel('Periods')
subplot(1,2,2)
plot(j,x2(1:T),'Color',[0.5 0.5 0.5],'linewidth',2.5)
title('Armament stock country 2')
xlabel('Periods')
