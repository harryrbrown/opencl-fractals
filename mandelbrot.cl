#pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable

__kernel void mandelbrot(__global {0} *coord, __global ushort *matrix, ushort const iterations)
{{
	{1} tempReal, real = 0;
	{1} imaginary = 0;
	int globalID = get_global_id(0);
	matrix[globalID] = 0;

	int count = 0;
	for (count; count < iterations; count++)
	{{
		tempReal = real*real - imaginary*imaginary + coord[globalID].x;
		imaginary = 2* real*imaginary + coord[globalID].y;
		real = tempReal;
		if (fabs(real) + fabs(imaginary) > 2.0{2})
		{{
			 matrix[globalID] = count;
		}}
	}}
}}