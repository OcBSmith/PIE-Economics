% ***********************************************
% An Introduction to Computational Macroeconomics
% A. Bongers, T. Gómez and J. L. Torres (2019)
% Dynamic IS-LM model in MATLAB
% File: m2.m
% ***********************************************
clear all

% Periods
T = 30;

% Exogenous variables
Beta0 = 2100;
m0 = 100;
ypot0 = 2000;

% Parameters
Theta = 0.5;
Psi = 0.01;
Beta1 = 50;
Mi = 0.01;
Ni = 0.2;

%Matrices
A=[0 Mi;-Ni*Beta1/Theta Ni*(Beta1*Mi-Beta1*Psi/Theta-1)];
B=[0 0 -Mi; Ni Ni*Beta1/Theta -Ni*Beta1*Mi];
Z=[Beta0 m0 ypot0];

%Steady state
pbar = (Theta*Beta0)/Beta1+m0-(Psi+Theta/Beta1)*ypot0;
ybar = ypot0;
dp(1) = 0;
dy(1) = 0;
p(1) = pbar;
y(1) = ybar;
i(1) = -(1/Theta)*(m0-p(1)-Psi*y(1));
yd(1) = Beta0-Beta1*(i(1)-dp(1));

% Proper values
v=eig(A);
Lambda1=v(1);
Lambda2=v(2);

% Disturbance
m1= 101;

% Dynamics
for j=1:T;
y(j+1) = y(j)+dy(j);
p(j+1) = p(j)+dp(j);
dp(j+1) = Mi*(y(j+1)-ybar);
i(j+1) = -(1/Theta)*(m1-p(j+1)-Psi*y(j+1));
yd(j+1) = Beta0-Beta1*(i(j+1)-dp(j+1));
dy(j+1) = Ni*(yd(j+1)-y(j+1));
end;

% Graphics
j=1:T+1;
subplot(2,2,1)
plot(j,y,'Color',[0.25 0.25 0.25],'linewidth',3.5)
xlabel('Periods')
title('Production')
subplot(2,2,2)
plot(j,yd,'Color',[0.25 0.25 0.25],'linewidth',3.5)
xlabel('Periods')
title('Aggregate Demand')
subplot(2,2,3)
plot(j,p,'Color',[0.25 0.25 0.25],'linewidth',3.5)
xlabel('Periods')
title('Prices')
