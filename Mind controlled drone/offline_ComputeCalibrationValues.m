x = O1;

NFFT = 2048;
Fs = 128;
freq = Fs/2*linspace(0,1,NFFT/2+1);
power_2 = 2*abs(fft(x)).^2/(NFFT^2);
power_1 = 2*abs(fft(x))/(NFFT);
logpower2 = 10*log10(power_2);
logpower1 = 10*log10(power_1);

ind = find(freq>8 & freq<12);
v1 = max(power_2(ind));
v2 = max(power_1(ind));
v3 = max(logpower2(ind));
v4 = max(logpower1(ind));

sprintf('Value for linear/squared spectrum: %.2f;\n Value for linear/no square spectrum: %.2f;\n Value for log/squared spectrum: %.2f;\n Value for log/no square spectrum: %.2f;\n ',...
    v1,v2,NaN,v4)