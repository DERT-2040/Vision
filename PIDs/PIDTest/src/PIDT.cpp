/*
 * PIDT.cpp
 *
 *  Created on: Jul 5, 2018
 *      Author: FIRSTMentor
 */

#include "PIDT.h"

PIDT::PIDT(float Px, float Ix, float Dx) {
	P = Px;
	I = Ix;
	D = Dx;

	error = 0;
	setpoint = 0;
	resultant = 0;
	integral = 0;
	derivative = 0;
	previous_error = 0;

}

void PIDT::setSetpoint(float setpoint)
{
	this->setpoint = setpoint;
}

double PIDT::runPID(double input)
{
	if(continuous == true)
	{

		previous_error = error;
		error = setpoint-input;

		if(error > 180)
		{
			error = -1*(maximum-setpoint-input);
		}
		else if(error < -180)
		{
			error = maximum - input + setpoint - minimum;
		}
		else
		{
			error = (setpoint - input);
		}

		integral += (error*.02);

		derivative = (error - previous_error) / .02;

		resultant = P*error + I*integral + D*derivative;

		if(resultant > 1)
		{
			resultant = 1;
		}

	}
	else
	{
		previous_error = error;

		error = (setpoint - input);

		integral += (error*.02);

		derivative = (error-previous_error) / .02;

		resultant = P*error + I*integral + D*derivative;

		if(resultant > 1)
		{
			resultant = 1;
		}
	}

	return resultant;

}

void PIDT::setContinuous(bool contin)
{
	continuous = contin;
}

void PIDT::setRange(float min, float max)
{
	minimum = min;
	maximum = max;
}

PIDT::~PIDT() {
	// TODO Auto-generated destructor stub
}

