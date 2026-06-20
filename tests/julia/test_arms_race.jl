using Test
using MacroAIComp

@testset "ArmsRace Tests" begin
    global_stability_params = ArmsRaceParams(0.50, 0.25, 0.25, 0.50, 1.00, 1.00)
    saddle_path_params = ArmsRaceParams(0.25, 0.50, 0.50, 0.25, 1.00, 1.00)

    @testset "Steady State" begin
        # Matches test_steady_state_matches_book_table_1_1
        res = steady_state(global_stability_params, [1.0, 1.0])
        @test res ≈ [4.0, 4.0] atol=1e-6

        # Matches test_sensitivity_analysis_alpha_0_7_matches_book_section_1_6_1
        params = ArmsRaceParams(0.70, 0.25, 0.25, 0.50, 1.00, 1.00)
        res_sens = steady_state(params, [1.0, 1.0])
        @test res_sens ≈ [2.61, 3.30] atol=1e-2

        # Matches test_saddle_path_steady_states_match_book_section_1_6_2
        initial = steady_state(saddle_path_params, [-1.0, -1.0])
        final = steady_state(saddle_path_params, [-0.5, -1.0])
        @test initial ≈ [4.0, 4.0] atol=1e-6
        @test final ≈ [3.33, 2.67] atol=1e-2
    end

    @testset "Eigenvalues" begin
        # Matches test_eigenvalues_match_book_section_1_3_2
        eigs = eigenvalues(global_stability_params)
        @test sort(eigs) ≈ [-0.75, -0.25] atol=1e-6

        # Matches test_sensitivity_analysis_eigenvalues
        params = ArmsRaceParams(0.70, 0.25, 0.25, 0.50, 1.00, 1.00)
        eigs_sens = eigenvalues(params)
        @test sort(eigs_sens) ≈ [-0.87, -0.33] atol=1e-2
    end

    @testset "Stability & Classification" begin
        # Matches test_global_stability_calibration_is_not_a_saddle_path
        @test !is_saddle_path(global_stability_params)

        # Matches test_saddle_path_calibration_is_detected
        @test is_saddle_path(saddle_path_params)
    end

    @testset "Simulation" begin
        # Matches test_shock_analysis_new_steady_state_matches_book_section_1_5
        x1, x2 = simulate(global_stability_params, [1.0, 1.0], [2.0, 1.0], 200, 2)
        @test [x1[end], x2[end]] ≈ [6.67, 5.33] atol=1e-2

        # Matches test_shock_analysis_starts_at_initial_steady_state
        x1_init, x2_init = simulate(global_stability_params, [1.0, 1.0], [2.0, 1.0], 30, 2)
        @test [x1_init[1], x2_init[1]] ≈ [4.0, 4.0] atol=1e-6

        # Matches test_saddle_path_jump_matches_book_section_1_6_2
        x1_saddle, x2_saddle = simulate_saddle_path(
            saddle_path_params,
            [-1.0, -1.0],
            [-0.5, -1.0],
            200,
            2,
            1, # jump_variable 1 in Julia
        )
        @test x1_saddle[2] ≈ 2.0 atol=1e-2
        @test [x1_saddle[end], x2_saddle[end]] ≈ [3.33, 2.67] atol=1e-2

        # Matches test_simulate_saddle_path_raises_for_non_saddle_calibration
        @test_throws ArgumentError simulate_saddle_path(
            global_stability_params, [1.0, 1.0], [2.0, 1.0]
        )
    end
end
