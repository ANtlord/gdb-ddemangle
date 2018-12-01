import core.stdc.stdio;
import core.demangle;
import std.string;

extern(C) auto dem(char *str)
{
	auto res = demangle(str.fromStringz());
	return res.toStringz;
}
