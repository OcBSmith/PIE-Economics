% ***********************************************
% An Introduction to Computational Macroeconomics
% A. Bongers, T. Gómez and J. L. Torres (2019)
% An example of a dynamic system in MATLAB
% Richardson's arms race model
% File: m1.m
%
% Transcribed verbatim from Appendix B of the book. This is the
% numerical oracle for practica P0: our Python/Julia ports must
% reproduce the steady state, eigenvalues and trajectories computed
% here for the same calibration.
% ***********************************************
clear all

% Periods
T = 30;

% Model parameters
Alpha = 0.50;
Beta = 0.25;
Gamma = 0.25;
Delta = 0.50;
Theta = 1.00;
Ita = 1.00;

% Value of exogenous variables
z1 = 1;
z2 = 1;

% Matrices
A=[-Alpha Beta; Gamma -Delta];
B=[Theta 0; 0 Ita];
z=[z1; z2];

% Steady state
EE = -A^(-1)*B*z;
x1(1) = EE(1);
x2(1) = EE(2);
dx1(1) = 0;
dx2(1) = 0;

% Eigenvalues
v=eig(A);
Lambda1=v(1);
Lambda2=v(2);

% Shocks
%z1 = 2;
%Alpha = 0.7;

% Dynamics
for i=1:T-1;
x1(i+1) = x1(i)+dx1(i);
x2(i+1) = x2(i)+dx2(i);
dx1(i+1) = -Alpha*x1(i+1)+Beta*x2(i+1)+Theta*z1;
dx2(i+1) = Gamma*x1(i+1)-Delta*x2(i+1)+Ita*z2;
end;

% Graphics
j=1:T;
subplot(1,2,1)
plot(j,x1,'Color',[0.25 0.25 0.25],'linewidth',3.5)
title('Variable x1')
xlabel('Periods')
subplot(1,2,2)
plot(j,x2,'Color',[0.25 0.25 0.25],'linewidth',3.5)
title('Variable x2')
xlabel('Periods')

% Phase diagram
syms x1 x2;
[x1 x2]=meshgrid(0:1:10, 0:1:10);
dx1 = -Alpha*x1+Beta*x2+Theta*z1;
dx2 = Gamma*x1-Delta*x2+Ita*z2;
figure;
quiver(x1,x2,dx1,dx2);
title('Phase Diagram: Richardson Model')
xlabel('Variable x1')
ylabel('Variable x2')
hold on
grid on
plot(EE(1),EE(2),'o','Color',[0 0 0])

% Trajectory
figure
quiver(x1,x2,dx1,dx2);
title('Richardson Model: Trajectory to the Steady State')
xlabel('Variable x1')
ylabel('Variable x2')
hold on
y=[10; 8];
n=20;
d=@(x1,x2) [-Alpha*x1+Beta*x2+Theta*z1; Gamma*x1-Delta*x2+Ita*z2];
for i=1:n
yy = y+d(y(1),y(2));
plot([y(1),yy(1)],[y(2),yy(2)],'o-','Color',[0 0 0])
y=yy;
end
