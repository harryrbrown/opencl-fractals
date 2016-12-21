#pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable

__kernel void julia(__global {0} *coord, __global ushort *matrix, ushort const iterations)
{{
	int globalID = get_global_id(0);
	matrix[globalID] = 0;
	{1} tempReal, real = coord[globalID].x;
	{1} imaginary = coord[globalID].y;

	int count = 0;
	for(count; count < iterations; count++)
	{{
		tempReal = real*real - imaginary*imaginary - 0.8;
		imaginary = 2* real*imaginary + 0.156;
		real = tempReal;
		if (fabs(real) + fabs(imaginary) > 2.0{2})
		{{
			 matrix[globalID] = count;
		}}
	}}
}}