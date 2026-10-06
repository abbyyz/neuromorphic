%% Read in Data 

%Lamp Spectra
rawLamp = readmatrix('Summary.xlsx','Sheet','Lamp','Range','A3:B803');
filter_375SC01 = readmatrix('Summary.xlsx','Sheet','Lamp','Range','D3:E803');

%MFM
%Mo_10MFM = readmatrix('Summary.xlsx','Sheet','MFM','Range','A3:B803');
%TiN_10MFM = readmatrix('Summary.xlsx','Sheet','MFM','Range','D3:E803');
VO2_MFM = readmatrix('Summary.xlsx', 'Sheet', 'MFM', 'Range', 'A3:B803')

%Collabs
%Absorptance of Perovskite films from Brittany - 07062026
%pero = readmatrix('Summary.xlsx','Sheet','Collabs','Range','A3:B803');


%% Multiply Spectra with MFM abs 
% raw_Mo = rawLamp(:,2) .* Mo_10MFM(:,2); 
% filter_375SC01_Mo = filter_375SC01(:,2) .* Mo_10MFM(:,2); 

raw_TiN = rawLamp(:,2) .* VO2_MFM(:,2); 
%filter_375SC01_TiN = filter_375SC01(:,2) .* TiN_10MFM(:,2); 

%Collabs: 
raw_Pero = rawLamp(:,2) .* pero(:,2); 

%% Integrate 

%Spectra 
i_rawLamp = trapz(rawLamp(101:601,1),rawLamp(101:601,2)); 
%i_filter_375SC01 = trapz(filter_375SC01(:,1),filter_375SC01(:,2)); 

%MFM
% i_raw_Mo = trapz(rawLamp(:,1),raw_Mo); 
% i_filter_375SC01_Mo = trapz(filter_375SC01(:,1),filter_375SC01_Mo); 
% 
% abs_raw_Mo = i_raw_Mo / i_rawLamp; 
% abs_filter_Mo = i_filter_375SC01_Mo / i_filter_375SC01; 
% 
% i_raw_TiN = trapz(rawLamp(:,1),raw_TiN); 
% i_filter_375SC01_TiN = trapz(filter_375SC01(:,1),filter_375SC01_TiN); 

%Collabs
i_raw_pero = trapz(pero(:,1),raw_Pero); 

%Normalize
% abs_raw_TiN = i_raw_TiN / i_rawLamp; 
% abs_filter_TiN = i_filter_375SC01_TiN / i_filter_375SC01; 
abs_raw_per = i_raw_pero / i_rawLamp; 

%% Plot 

%Mo 
% tiledlayout(2,1)
% nexttile
% plot(rawLamp(:,1),rawLamp(:,2),'LineWidth',1.5,'DisplayName','Lamp'); 
% hold on 
% plot(rawLamp(:,1),raw_Mo,'LineWidth',1.5,'DisplayName','Lamp x Mo Abs'); 
% xlabel('Wavelength (nm)'); 
% ylabel('Spectral Irr'); 
% legend
% title('Full Lamp Spectra')
% 
% nexttile
% plot(filter_375SC01(:,1),filter_375SC01(:,2),'LineWidth',1.5,'DisplayName','Lamp'); 
% hold on 
% plot(filter_375SC01(:,1),filter_375SC01_Mo,'LineWidth',1.5,'DisplayName','Lamp x Mo Abs'); 
% xlabel('Wavelength (nm)'); 
% ylabel('Spectral Irr'); 
% legend
% title('375 nm Filter Lamp Spectra')

% %TiN
% tiledlayout(2,1)
% nexttile
% plot(rawLamp(:,1),rawLamp(:,2),'LineWidth',1.5,'DisplayName','Lamp'); 
% hold on 
% plot(rawLamp(:,1),raw_TiN,'LineWidth',1.5,'DisplayName','Lamp x TiN Abs'); 
% xlabel('Wavelength (nm)'); 
% ylabel('Spectral Irr'); 
% legend
% title('Full Lamp Spectra')
% 
% nexttile
% plot(filter_375SC01(:,1),filter_375SC01(:,2),'LineWidth',1.5,'DisplayName','Lamp'); 
% hold on 
% plot(filter_375SC01(:,1),filter_375SC01_TiN,'LineWidth',1.5,'DisplayName','Lamp x TiN Abs'); 
% xlabel('Wavelength (nm)'); 
% ylabel('Spectral Irr'); 
% legend
% title('375 nm Filter Lamp Spectra')

%collabs
%Pero 
figure()
yyaxis left 
plot(pero(:,1),raw_Pero); 
hold on 
yyaxis right 
plot(pero(:,1),pero(:,2)); 