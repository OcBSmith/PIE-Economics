% ***********************************************
% An Introduction to Computational Macroeconomics
% A. Bongers, T. Gómez and J. L. Torres (2019)
% Dynamic IS-LM model in DYNARE
% File: m2d.mod
% ***********************************************

// Endogenous variables
var p y yd i dy dp;

// Exogenous variables
varexo m, beta0, ybar0;

// Parameters
parameters psi, theta, beta1, mi, ni;

theta = 0.5;
psi = 0.05;
beta1 = 50;
mi = 0.01;
ni = 0.2;

// Model equations
model;
m-p=psi*y-theta*i;
yd=beta0-beta1*(i-dp);
dp=mi*(y-ybar0);
dy=ni*(yd-y);
dp(-1)=p-p(-1);
dy(-1)=y-y(-1);
end;

// Initial values
initval;
y = ybar0;
yd = y;
p = 1;
i = 1;
dy = 0;
dp = 0;
m = 100;
beta0 = 2100;
ybar0 = 2000;
end;

steady;
check;
shocks;
var m;
periods 1:30;
values 101;
end;
simul(periods=30);
